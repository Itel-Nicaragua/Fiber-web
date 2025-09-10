
import os
from flask import redirect, request, session
from functools import wraps
from flask.helpers import flash
from conexion import get_sqlserver_engine1
import pandas as pd
from datetime import datetime
import locale
from sqlalchemy import text



def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin") == 1:
            return """<h3 class="p-5" style="
            color: red;
            margin: 2%;
            font-size: 6vh;
            width: fit-content;
            ">No tienes permiso para acceder a este recurso</h3>""", 403
        return f(*args, **kwargs)
    return decorated_function


def validarString(dato):
    if not dato or not dato.isalpha() or dato.isspace():
        return False

    return True


def validarDouble(dato):
    if not dato or not dato.replace(".", "").isdigit() or float(dato) < 1:
        return False

    return True

def exportar_historial(fecha_inicio, fecha_final):
    engine = get_sqlserver_engine1()
    query = text("""
        SELECT * FROM vw_llamadas_completa
        WHERE convert(date, fecha_registro) BETWEEN :fecha_inicio AND :fecha_final ORDER BY fecha_registro
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"fecha_inicio": fecha_inicio, "fecha_final": fecha_final})
        rows = result.fetchall()
        df = pd.DataFrame(rows, columns=result.keys())
    return df

def exportar_historial_telemarketing(fecha_inicio, fecha_final):
    engine = get_sqlserver_engine1()
    query = text("""
        SELECT * FROM telemarketing
        WHERE fecha BETWEEN :fecha_inicio AND :fecha_final ORDER BY fecha
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"fecha_inicio": fecha_inicio, "fecha_final": fecha_final})
        rows = result.fetchall()
        df = pd.DataFrame(rows, columns=result.keys())
    return df

def exportar_base_total(fecha_inicio, fecha_final):
    engine = get_sqlserver_engine1()
    query = text("""
        SELECT * FROM actual
        WHERE convert(date, fecha_suscripcion) BETWEEN :fecha_inicio AND :fecha_final ORDER BY fecha_suscripcion
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"fecha_inicio": fecha_inicio, "fecha_final": fecha_final})
        rows = result.fetchall()
        df = pd.DataFrame(rows, columns=result.keys())
    return df


def formatear_fecha(fecha):
    for loc in ['es_ES.utf8', 'es_ES.UTF-8', 'es_ES', 'spanish']:
        try:
            locale.setlocale(locale.LC_TIME, loc)
            break
        except locale.Error:
            continue
    else:
        print("No se pudo configurar locale en español")

    return fecha.strftime("%d de %B %Y, %H:%M")
