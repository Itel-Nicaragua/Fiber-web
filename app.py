from datetime import date, datetime
import os
import requests
from dotenv import load_dotenv
from flask import Flask, json, session, url_for, make_response, render_template_string
from flask_session import Session
from flask import Flask, flash, redirect, render_template, request, session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import admin_required, login_required, exportar_historial, exportar_historial_telemarketing, exportar_base_total, formatear_fecha
from flask import jsonify, send_file
import pyodbc
import tempfile
from conexion import get_sqlserver_connection1, get_mysql_connection, get_oracle_connection
from math import ceil
import math
import pdfkit
from datetime import datetime, timedelta
import logging
import time


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
            cursor.execute(f"SELECT id, username, pass, active, rol, id_admin_ticket FROM users WHERE username = ?", username)
            row = cursor.fetchone()

            if not row:
                flash("Nombre o contraseña incorrectos", "error")
                return render_template("login.html")

            id, user_name, hashed_pass, is_active, rol, id_admin_ticket = row

            cursor.execute("INSERT INTO ingresos_users (name_user, fecha_ingreso) VALUES (?, GETDATE())", user_name)
            conn.commit()

            cursor.close()
            conn.close()

            
            if is_active != 1:
                flash("Usuario inactivo, contacte a un administrador", "error")
                return render_template("login.html")

            if not check_password_hash(hashed_pass, password):
                flash("Nombre o contraseña incorrectos", "error")
                return render_template("login.html")
            
            session["user_id"] = id
            session["user_name"] = user_name
            session["rol"] = rol
            session["id_admin_ticket"] = id_admin_ticket

            return redirect("/")

        except Exception as e:
            flash("Error de conexión con la base de datos", "error")
            logging.error(f"Error en login: {e}", exc_info=True)
            return render_template("login.html")

    else:
        return render_template("login.html")

        
@app.route("/")
@login_required
def index():

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

        if not page:
            page = 1

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
        logging.error(f"Error en index: {e}", exc_info=True)
        return render_template("index.html")

# Mapa de códigos a nombres legibles
TIPOS_EXPORT = {
    "BT": "base_total",
    "BL": "llamadas",
    "BTM": "historial_telemarketing"
}

@app.route("/export_excel", methods=["POST"])
@login_required
def export_excel():
    tipo  = request.form.get("tipo-export")
    inicio = request.form.get("start")
    final  = request.form.get("end")

    if not tipo:
        flash("Debe seleccionar un tipo de exportación", "error")
        return redirect("/")
    if not inicio or not final:
        flash("Debe seleccionar ambas fechas", "error")
        return redirect("/")

    # Genera el DataFrame según el tipo
    if tipo == "BT":
        df = exportar_base_total(inicio, final)
    elif tipo == "BL":
        df = exportar_historial(inicio, final)
    elif tipo == "BTM":
        df = exportar_historial_telemarketing(inicio, final)
    else:
        flash("Tipo de exportación no válido", "error")
        return redirect("/")

    # Nombre legible según el tipo
    nombre_tipo = TIPOS_EXPORT.get(tipo, "exportacion")
    # Fecha en formato YYYYMMDD
    fecha_descarga = datetime.now().strftime("%Y%m%d")
    # Construye el nombre final
    filename = f"{nombre_tipo}_{fecha_descarga}.xlsx"

    return descargar_excel(df, filename)


def descargar_excel(df, filename):
    """
    Crea un archivo temporal .xlsx a partir del DataFrame y lo envía
    con el nombre que le pasemos en 'download_name'.
    """
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(temp.name, index=False)

    return send_file(
        temp.name,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")

@app.route("/404")
def errorPage():
    return render_template("404.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/info_cliente/<numero>/", methods=["GET", "POST"])
@login_required
def info_cliente(numero):

    # Validar que sea un número
    if not numero.isdigit():
        return redirect('/404')  # redirige a 404 si no es número
    
    conn = get_sqlserver_connection1()
    cursor = conn.cursor()

    # Obtener columnas de la tabla 'actual'
    cursor.execute(f"SELECT * FROM actual WHERE numero = {numero}")
    columnas_actual = [col[0] for col in cursor.description]
    fila_actual = cursor.fetchone()

    if not fila_actual:
        return redirect('/404')  # redirige si no se encuentra el registro

    if fila_actual:
        datos = {col: (val if val is not None else "") for col, val in zip(columnas_actual, fila_actual)}
    else:
        datos = {}

    # Obtener columnas de la tabla 'llamadas'
    cursor.execute(f"SELECT l.*, u.name FROM llamadas l INNER JOIN users u ON usuario_id = u.id WHERE id_cliente = {fila_actual.id} ORDER BY fecha_registro DESC")
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
        "Baja Fin de Contrato",
        "Baja Voluntaria",
        "Cobranza Activa",
        "Falta de información PBDC",
        "Reporte al Buro",
        "Saneado Interno"
    ]

    conn = get_mysql_connection()
    cursor = conn.cursor()
    start = time.time()

    cursor.execute(f"""SELECT postventa.*, place, price FROM postventa
    LEFT JOIN Customers ON id_customer = id_cliente
    LEFT JOIN places ON places.id_place = postventa.id_place
    LEFT JOIN bandwidth_price ON id_price_new = bandwidth_price.id_bandwidth_price
    WHERE service_number = {numero} ORDER BY date_created DESC
    """)

    post_venta = cursor.fetchall()

    cursor.close()
    conn.close()

    estado_cuenta = get_estado_cuenta(numero)

    return render_template("info_cliente.html", datos=datos, llamadas = llamadas, motivos_estado=motivos_estado, estado_cuenta=estado_cuenta, post_venta=post_venta)
    
    

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

    motivos_estado = [
        {"id": 18, "estado": "Baja Voluntaria"},
        {"id": 19, "estado": "Baja Administrativa Sin Penalización"},
        {"id": 21, "estado": "Baja Fin de Contrato"},
        {"id": 23, "estado": "Reporte al Buro"},
    ]

    estado_a_id = {m["estado"]: m["id"] for m in motivos_estado}

    if estado in estado_a_id:
        conn = get_mysql_connection()
        cursor = conn.cursor()

        cursor.execute(f"SELECT id_customer FROM Customers WHERE service_number = {numero}")
        row = cursor.fetchone()

        if row:

            id_customer = row['id_customer']
            id_estado = estado_a_id[estado]
            id_user = session['id_admin_ticket']

            query = """
            INSERT INTO Customers_proccess
            (id_customer, id_status, id_user, date_approval, comments_approval, is_approval)
            VALUES (%s, %s, %s, NOW(), %s, 1)
            """

            values = (id_customer, id_estado, id_user, comentario)

            cursor.execute(query, values)

            cursor.execute(f"UPDATE Customers SET id_status = %s WHERE id_customer = {id_customer}", id_estado)

            conn.commit()

        else:
            flash("Linea no encontrada en sistema de tickets", "error")
            return redirect(request.url)  

    flash("Estado reportado satisfactoriamente", "exito")
    return redirect(f"/info_cliente/{numero}")

def parse_fecha(fecha_str):
    for fmt in ("%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(fecha_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Formato de fecha inválido: {fecha_str}")

@app.route('/insertar_llamada', methods=['POST'])
@login_required
def insertar_llamada():
    id_cliente  = request.args.get('id')
    gestion_cobro = request.form.get('gestion_cobro')
    herramienta_cobro = request.form.get('herramienta_cobro')
    motivo_macro = request.form.get('motivo_macro')
    motivo_micro = request.form.get('motivo_micro')
    proxima_llamada = request.form.get('proxima_llamada')
    proxima_llamada = proxima_llamada or None

    if proxima_llamada:
        fecha = datetime.strptime(proxima_llamada, "%Y-%m-%d")
        proxima_llamada = fecha

    estado_llamada = request.form.get('estado_llamada')
    comentario = request.form.get('comentarios')
    usuario = session['user_id']
    rol = session['rol']

    # Área según rol
    area_map = {0: 'CyC', 1: 'SAD', 2: 'Tiendas', 3: 'Telemarketing'}
    area = area_map.get(rol, 'Desconocido')

    conn = get_sqlserver_connection1()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO llamadas (
                proxima_llamada, estado_llamada, comentarios,
                usuario_id, fecha_registro, gestion_cobro,
                herramienta_cobro, motivo_macro, motivo_micro, id_cliente
        ) VALUES (?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, ?)

    """, (
        proxima_llamada,
        estado_llamada,
        comentario,
        usuario,
        gestion_cobro,
        herramienta_cobro,
        motivo_macro,
        motivo_micro,
        id_cliente
    ))

    conn.commit()

    cursor.close()
    conn.close()
    flash("Llamada registrada correctamente", "exito")
    return redirect(request.referrer)

def get_estado_cuenta(numero):
    conn = get_oracle_connection()
    cursor = conn.cursor()

    consulta = """
    SELECT TO_DATE(SUBSTR(LTRIM(TO_CHAR(r.reqtime)), 1, 8), 'YYYYMMDD') as fecha,
           r.deductamt as monto
    FROM XBOSS1.xb_transfer_detail r
    WHERE r.desttelno = :destino
    ORDER BY fecha DESC
    """
    destino = '00505' + numero 
    cursor.execute(consulta, destino=destino)
    pagos = cursor.fetchall()

    columnas = [col[0].lower() for col in cursor.description]
    pagos_dict = [dict(zip(columnas, fila)) for fila in pagos]

    # Formatear fecha como string legible
    for f in pagos_dict:
        f['fecha_str'] = f['fecha'].strftime('%d/%m/%Y')

    # Calcular total pagado
    total_pagado = sum(f['monto'] if f['monto'] is not None else 0 for f in pagos_dict)

    hoy = datetime.today()
    año_actual, mes_actual = hoy.year, hoy.month

    # Mes pasado
    if mes_actual == 1:
        mes_pasado, año_pasado = 12, año_actual - 1
    else:
        mes_pasado, año_pasado = mes_actual - 1, año_actual

    # Filtrar y sumar
    pago_mes_actual = sum(
        f["monto"] or 0
        for f in pagos_dict
        if f["fecha"].year == año_actual and f["fecha"].month == mes_actual
    )

    pago_mes_pasado = sum(
        f["monto"] or 0
        for f in pagos_dict
        if f["fecha"].year == año_pasado and f["fecha"].month == mes_pasado
    )

    consulta = """
    SELECT
    TO_DATE(SUBSTR(LTRIM(TO_CHAR(ac.ADJUSTTIME)), 1, 8), 'YYYYMMDD') AS fecha,
    ac.ADJUSTFEENUM AS monto,
    ac.ADJUSTFEETYPE AS tipo,
    ac.ADJUSTREASON AS comentario
    FROM BOSS3_CRM1.ADJUST_ACCOUNT_DETAIL ac
            INNER JOIN BOSS3.CM_SUBSCRIBER_0 s
                        ON s.SUBSCRIBER_UID = ac.SUBSCRIBERID
    AND s.PHONE_NO = :destino
    ORDER BY fecha DESC
    """

    cursor.execute(consulta, destino=destino)
    ajustes = cursor.fetchall()

    columnas = [col[0].lower() for col in cursor.description]
    ajustes_dict = [dict(zip(columnas, fila)) for fila in ajustes]

    # Formatear fecha como string legible
    for f in ajustes_dict:
        f['fecha_str'] = f['fecha'].strftime('%d/%m/%Y')

    # Calcular total pagado
    total_ajustes_positivos = sum(f['monto'] if f['monto'] is not None and f['tipo'] != 3 else 0 for f in ajustes_dict)
    total_ajustes_negativos = sum(f['monto'] if f['monto'] is not None and f['tipo'] != 2 else 0 for f in ajustes_dict)
    
    consulta = """
    SELECT NVL(SUM(di.rec_amt), 0) AS total_debt
    FROM xboss1.cm_subs_subscriber ai
            JOIN xboss1.acct_unwoff di ON ai.subsid = di.subs_id
    WHERE ai.servnumber = :destino
    """

    cursor.execute(consulta, destino=destino)
    deuda = cursor.fetchone()[0]
    
    # Devolver todo en un diccionario
    resultado = {
        "pagos": pagos_dict,
        "total_pagado": total_pagado,
        "ajustes": ajustes_dict,
        "total_ajustes_positivos": total_ajustes_positivos,
        "total_ajustes_negativos": total_ajustes_negativos,
        "deuda": deuda,
        "mes_actual": pago_mes_actual,
        "mes_pasado": pago_mes_pasado,
    }

    return resultado


