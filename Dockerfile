FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema + locales
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
    locales

# Generar locale en español
RUN locale-gen es_ES.UTF-8

# Establecer variables de entorno para el locale
ENV LANG=es_ES.UTF-8
ENV LANGUAGE=es_ES:es
ENV LC_ALL=es_ES.UTF-8

# Limpiar cache de apt
RUN rm -rf /var/lib/apt/lists/*

# Clave pública de Microsoft y repositorio para ODBC
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list

# Instalar el driver ODBC de Microsoft
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*

# Copiar la carpeta ya descomprimida de Instant Client
COPY instantclient_19_28 /usr/lib/oracle/instantclient/instantclient_19_28

# Variables de entorno para Oracle Instant Client
ENV LD_LIBRARY_PATH=/usr/lib/oracle/instantclient/instantclient_19_28:$LD_LIBRARY_PATH
ENV ORACLE_HOME=/usr/lib/oracle/instantclient/instantclient_19_28

# Instalar dependencias de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
