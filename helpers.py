
import os
from flask import redirect, request, session
from functools import wraps
from flask.helpers import flash
from base64 import b64encode
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import docraptor
from conexion import get_sqlserver_connection1
import pandas as pd

ik = ImageKit(private_key='private_pbBN7H3s6r1YGqTsxPQqdelGb38=',
                public_key='public_rKkJyqI11fEPBRHq/2QD3PyJJwo=',
                url_endpoint='https://ik.imagekit.io/JefferssonVMT')

doc_api = docraptor.DocApi()
doc_api.api_client.configuration.username = '23md2lJdruKB9SQuJ2Pj'

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
    conn = get_sqlserver_connection1()
    query = """
        SELECT * FROM historial_llamadas
        WHERE fecha_llamada BETWEEN ? AND ? ORDER BY fecha_llamada
    """
    df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_final])
    conn.close()
    return df

def exportar_historial_telemarketing(fecha_inicio, fecha_final):
    conn = get_sqlserver_connection1()
    query = """
        SELECT * FROM telemarketing
        WHERE fecha BETWEEN ? AND ? ORDER BY fecha
    """
    df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_final])
    conn.close()
    return df

def exportar_base_total(fecha_inicio, fecha_final):
    conn = get_sqlserver_connection1()
    query = """
        SELECT * FROM actual
        WHERE fecha_suscripcion BETWEEN ? AND ? ORDER BY fecha_suscripcion
    """
    df = pd.read_sql(query, conn, params=[fecha_inicio, fecha_final])
    conn.close()
    return df