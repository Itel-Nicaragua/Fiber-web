# conexion.py
import pymysql
import pyodbc
import cx_Oracle

# SQL Server 1
SQL_SERVER_1_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': '172.16.120.5',
    'database': 'cartera_cobro',
    'uid': 'sa',
    'pwd': '1234'
}

# SQL Server 2
SQL_SERVER_2_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': '192.168.128.32',
    'database': 'SolarWindsOrion',
    'uid': 'icrm_comercial',
    'pwd': '(&q2M`2qX$XVk,%XW%e9'
}

# MySQL
MYSQL_CONFIG = {
    'host': '172.16.120.74',
    'user': 'root',
    'password': 'Perseo2016',
    'database': 'NOC_Ticket'
}

# Oracle
ORACLE_CONFIG = {
    'user': 'query_user',
    'password': 'poi098asd!@#',
    'dsn': '172.16.1.14:1521/testscan'
}

# ---------- FUNCIONES DE CONEXIÓN -----------

def get_sqlserver_connection1():
    conn_str = (
        f"DRIVER={SQL_SERVER_1_CONFIG['driver']};"
        f"SERVER={SQL_SERVER_1_CONFIG['server']};"
        f"DATABASE={SQL_SERVER_1_CONFIG['database']};"
        f"UID={SQL_SERVER_1_CONFIG['uid']};"
        f"PWD={SQL_SERVER_1_CONFIG['pwd']}"
    )
    return pyodbc.connect(conn_str)


def get_sqlserver_connection2():
    conn_str = (
        f"DRIVER={SQL_SERVER_2_CONFIG['driver']};"
        f"SERVER={SQL_SERVER_2_CONFIG['server']};"
        f"DATABASE={SQL_SERVER_2_CONFIG['database']};"
        f"UID={SQL_SERVER_2_CONFIG['uid']};"
        f"PWD={SQL_SERVER_2_CONFIG['pwd']}"
    )
    return pyodbc.connect(conn_str)


def get_mysql_connection():
    return pymysql.connect(
        host=MYSQL_CONFIG['host'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        database=MYSQL_CONFIG['database'],
        cursorclass=pymysql.cursors.DictCursor
    )


def get_oracle_connection():
    return cx_Oracle.connect(
        ORACLE_CONFIG['user'],
        ORACLE_CONFIG['password'],
        ORACLE_CONFIG['dsn']
    )
