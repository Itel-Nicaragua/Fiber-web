import pyodbc
import bcrypt
from conexion import get_sqlserver_connection1
from werkzeug.security import generate_password_hash
# Obtener conexión a SQL Server
conn = get_sqlserver_connection1()
cursor = conn.cursor()

try:
    # Consultar datos de la tabla users
    cursor.execute("select * from users")
    users = cursor.fetchall()

    # Consulta SQL para insertar en users_new
    insert_query = """
    INSERT INTO users_new (username, pass, active, rol)
    VALUES (?, ?, ?, ?)
    """

    # Procesar cada usuario
    for user in users:
        username, password, status, role = user
        print(user)
        # Hashear la contraseña
        hashed_password = generate_password_hash(password)
        # Preparar los datos para la inserción
        data = (username, hashed_password, status, role)
        # Ejecutar la consulta
        cursor.execute(insert_query, data)

    # Confirmar los cambios
    conn.commit()
    print("Usuarios insertados exitosamente en users_new.")

except pyodbc.Error as err:
    print(f"Error: {err}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
        print("Conexión cerrada.")