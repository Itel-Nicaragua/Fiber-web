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

# Importar la clave pública de Microsoft y agregar el repositorio
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/microsoft.gpg && \
    curl -sSL https://packages.microsoft.com/config/debian/12/prod.list -o /etc/apt/sources.list.d/mssql-release.list

# Instalar el driver ODBC de Microsoft
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*

# Instalar Oracle Instant Client
RUN mkdir -p /usr/lib/oracle/
COPY instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip /tmp/
COPY instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip /tmp/
RUN unzip /tmp/instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip -d /usr/lib/oracle/ && \
    unzip /tmp/instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip -d /usr/lib/oracle/ && \
    rm /tmp/instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip /tmp/instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip

ENV LD_LIBRARY_PATH=/usr/lib/oracle/instantclient_19_28:$LD_LIBRARY_PATH
ENV ORACLE_HOME=/usr/lib/oracle/instantclient_19_28

# Instalar dependencias de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto
EXPOSE 5000

# Usar gunicorn para producción
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]