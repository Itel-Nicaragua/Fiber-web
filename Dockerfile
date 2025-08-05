FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libaio1 \
    unixodbc-dev \
    curl \
    gnupg2 \
    apt-transport-https \
    unzip \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Importar la clave pública de Microsoft y agregar el repositorio de forma segura
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list

# Instalar el driver ODBC de Microsoft
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*

# Copiar la carpeta ya descomprimida de Instant Client
COPY instantclient_19_28 /usr/lib/oracle/instantclient/instantclient_19_28

# Configurar variables de entorno para Oracle Instant Client
ENV LD_LIBRARY_PATH=/usr/lib/oracle/instantclient/instantclient_19_28:$LD_LIBRARY_PATH
ENV ORACLE_HOME=/usr/lib/oracle/instantclient/instantclient_19_28


# Instalar dependencias de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto
EXPOSE 5000

# Usar gunicorn para producción
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]