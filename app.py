from datetime import date, datetime
import os
import requests
from dotenv import load_dotenv
from flask import Flask, json, session, url_for
from flask_session import Session
from flask import Flask, flash, redirect, render_template, request, session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import admin_required, login_required, exportar_historial, exportar_historial_telemarketing, exportar_base_total, formatear_fecha
from flask import jsonify, send_file
import pyodbc
import tempfile
from conexion import get_sqlserver_connection1
from math import ceil
import math
import time
from datetime import datetime, timedelta

app = Flask(__name__)

app.jinja_env.filters["date"] = formatear_fecha

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = 'super secret key'

Session(app)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Debe ingresar un usuario", "error")
            return render_template("login.html")

        if not password:
            flash("Debe ingresar una contraseña", "error")
            return render_template("login.html")

        try:
            conn = get_sqlserver_connection1()
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, username, pass, active, rol FROM users_new WHERE username = ?", username)
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            if not row:
                flash("Nombre o contraseña incorrectos", "error")
                return render_template("login.html")

            id, user_name, hashed_pass, is_active, rol = row

            if not check_password_hash(hashed_pass, password):
                flash("Nombre o contraseña incorrectos", "error")
                return render_template("login.html")

            session["user_id"] = id
            session["user_name"] = user_name
            session["rol"] = rol

            return redirect("/")

        except Exception as e:
            flash("Error de conexión con la base de datos", "error")
            print(e)
            return render_template("login.html")

    else:
        return render_template("login.html")

        
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        try:
            page = int(request.args.get("page", 1))
            search_term = request.args.get("search", "").strip()
            filtro_fecha_param = request.args.get("filtro_fecha")
            filtro_dias = int(filtro_fecha_param) if filtro_fecha_param else None
            por_pagina = 15
            now = datetime.now()

            conn = get_sqlserver_connection1()
            cursor = conn.cursor()

            # Construir consulta base
            base_query = "FROM actual"
            where_clause = ""
            params = []

            if search_term:
                where_clause = "WHERE (Realname LIKE ? OR numero LIKE ?)"
                search_param = f"%{search_term}%"
                params = [search_param, search_param]
            
            if filtro_dias is not None:
                fecha_limite = now - timedelta(days=filtro_dias)
                if where_clause:
                    where_clause += " AND fecha_suscripcion >= ?"
                else:
                    where_clause = "WHERE fecha_suscripcion >= ?"
                params.append(fecha_limite)

            # Consulta para contar total (usando los mismos filtros)
            count_query = f"SELECT COUNT(*) {base_query} {where_clause}"
            cursor.execute(count_query, params) if params else cursor.execute(count_query)
            total_filas = cursor.fetchone()[0]
            total_paginas = math.ceil(total_filas / por_pagina)

            # Consulta para obtener datos (usando los mismos filtros)
            offset = (page - 1) * por_pagina
            data_query = f"""
                SELECT * {base_query} {where_clause}
                ORDER BY fecha_suscripcion DESC
                OFFSET {offset} ROWS
                FETCH NEXT {por_pagina} ROWS ONLY
            """
            
            if params:
                cursor.execute(data_query, params)
            else:
                cursor.execute(data_query)
                
            datos = cursor.fetchall()

            # Calcular el rango de páginas a mostrar
            start_page = max(1, page - 2)
            end_page = min(total_paginas, page + 2)

            cursor.close()
            conn.close()

            # Pasar parámetros para mantener los filtros en los links de paginación
            query_params = {}
            if search_term:
                query_params['search'] = search_term
            if filtro_dias:
                query_params['filtro_fecha'] = filtro_dias

            return render_template(
                "index.html",
                now=now,
                datos=datos,
                pagina=page,
                paginas=total_paginas,
                total=total_filas,
                mostrando_inicio=offset + 1,
                mostrando_fin=min(offset + por_pagina, total_filas),
                start_page=start_page,
                end_page=end_page,
                search_term=search_term,
                filtro_dias=filtro_dias,
                query_params=query_params  # Pasar los parámetros al template
            )

        except Exception as e:
            flash("Error de conexión con la base de datos", "error")
            print(e)
            return render_template("index.html")
    else:
        tipo = request.form.get("tipo-export")
        inicio = request.form.get("start")
        final = request.form.get("end")

        if not tipo:
            flash("Debe seleccionar un tipo de exportacion", "error")
            return redirect("/")
        if not inicio or not final:
            flash("Debe seleccionar ambas fechas", "error")
            return redirect("/")
        
        if tipo == "BT":
            df = exportar_base_total(inicio, final)
        
        elif tipo == "BL":
            df = exportar_historial(inicio, final)
        
        elif tipo == "BTM":
            df = exportar_historial_telemarketing(inicio, final)
            
        else:
            flash("Tipo de exportación no válido", "error")
            return redirect("/")

        return descargar_excel(df)
        



def descargar_excel(df):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(temp.name, index=False)

    return send_file(
        temp.name,
        as_attachment=True,
        download_name="historial.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")



@app.route("/info_cliente/<numero>/", methods=["GET", "POST"])
@login_required
def info_cliente(numero):
    conn = get_sqlserver_connection1()
    cursor = conn.cursor()

    # Obtener columnas de la tabla 'actual'
    cursor.execute(f"SELECT * FROM actual WHERE numero = {numero}")
    columnas_actual = [col[0] for col in cursor.description]
    fila_actual = cursor.fetchone()

    # Reemplazar None por "" en los datos de 'actual'
    if fila_actual:
        datos = {col: (val if val is not None else "") for col, val in zip(columnas_actual, fila_actual)}
    else:
        datos = {}

    # Obtener columnas de la tabla 'historial_llamadas'
    cursor.execute(f"SELECT * FROM historial_llamadas WHERE numero = {numero} ORDER BY fecha_registro DESC")
    columnas_llamadas = [col[0] for col in cursor.description]
    filas_llamadas = cursor.fetchall()

    # Reemplazar None por "" en los datos de 'llamadas'
    llamadas = [
        {col: (val if val is not None else "") for col, val in zip(columnas_llamadas, fila)}
        for fila in filas_llamadas
    ]

    cursor.close()
    conn.close()

    motivos_estado = [
        "Baja Administrativa Sin Penalización",
        "Baja Voluntaria",
        "Cobranza Activa",
        "Falta de información PBDC",
        "Reporte al Buro",
        "Saneado Interno"
    ]

    return render_template("info_cliente.html", datos=datos, llamadas = llamadas, motivos_estado=motivos_estado)
    
    

@app.route('/reportar_estado', methods=['POST'])
@login_required
def reportar_estado():
    numero  = request.args.get('numero')
    estado = request.form.get('estado')
    comentario = request.form.get('comentarios')

    if not estado:
        flash("Debe seleccionar un estado", "error")
        return redirect(request.url)  
    if not comentario:
        flash("Debe escribir un comentario", "error")
        return redirect(request.url)  
    
    conn = get_sqlserver_connection1()
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO reporte_estado (numero, estado, comentario, usuario, fecha_registro) VALUES (?, ?, ?, ?, GETDATE())", (numero, estado, comentario, session['user_name']))
    cursor.execute(f"UPDATE actual SET estado_final = ? WHERE numero = {numero}", estado)
    conn.commit()

    cursor.close()
    conn.close()

    print(f"Estado: {estado}, Comentario: {comentario}")
    flash("Estado reportado satisfactoriamente", "exito")
    return redirect(f"/info_cliente/{numero}")


@app.route('/insertar_llamada', methods=['POST'])
@login_required
def insertar_llamada():
    numero  = request.args.get('numero')
    gestion_cobro = request.form.get('gestion_cobro')
    motivo_macro = request.form.get('motivo_macro')
    motivo_micro = request.form.get('motivo_micro')
    proxima_llamada = request.form.get('proxima_llamada')
    estado_llamada = request.form.get('estado_llamada')
    comentario = request.form.get('comentarios')
    usuario = session['user_name']
    rol = session['rol']

    # Área según rol
    area_map = {0: 'CyC', 1: 'SAD', 2: 'Tiendas', 3: 'Telemarketing'}
    area = area_map.get(rol, 'Desconocido')

    conn = get_sqlserver_connection1()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO historial_llamadas (
            numero, numero_referido, canal_ventas, nombre_canal_ventas, FUR,
            suma_recargas, recarga_ajuste, NoReclamos, fecha_suscripcion,
            information_confirmation, Mes, AnchoBanda, precio, paquete, direccion,
            ciclo, Codigo_OA, departamento, antiguedad_meses, estatus_contrato,
            recarga_mes_anterior, recarga_mes_actual, deuda_icrm, estatus_orion,
            Proximo_Pago, ContactphoneNo, Realname, vigencia, distancia,
            fecha_renovacion, subsidio, Accion, estado_final, fecha_llamada,
            estado_llamada, Comentarios, usuario, fecha_registro, area,
            gestion_cobro, motivo_macro, motivo_micro
        )
        SELECT
            numero, numero_referido, canal_ventas, nombre_canal_ventas, FUR,
            suma_recargas, recarga_ajuste, NoReclamos, fecha_suscripcion,
            information_confirmation, Mes, AnchoBanda, precio, paquete, direccion,
            ciclo, Codigo_OA, departamento, antiguedad_meses, estatus_contrato,
            recarga_mes_anterior, recarga_mes_actual, deuda_icrm, estatus_orion,
            Proximo_Pago, ContactphoneNo, Realname, vigencia, distancia,
            fecha_renovacion, subsidio, Accion, estado_final,
            ?, ?, ?, ?, GETDATE(), ?, ?, ?, ?
        FROM actual
        WHERE numero = ?
    """, (
        proxima_llamada,
        estado_llamada,
        comentario,
        usuario,
        area,
        gestion_cobro,
        motivo_macro,
        motivo_micro,
        numero
    ))

    conn.commit()

    cursor.close()
    conn.close()
    flash("Llamada registrada correctamente", "exito")
    return redirect(f"/info_cliente/{numero}")



