FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para cx_Oracle y pyodbc
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libaio1 \
    unixodbc-dev \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip /tmp/
COPY instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip /tmp/

RUN unzip /tmp/instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip -d /usr/lib/oracle/instantclient \
    && unzip /tmp/instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip -d /usr/lib/oracle/instantclient \
    && rm /tmp/instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip /tmp/instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip
    

# Configurar variables de entorno para Oracle Instant Client
ENV LD_LIBRARY_PATH=/usr/lib/oracle/instantclient/instantclient_19_8:$LD_LIBRARY_PATH
ENV ORACLE_HOME=/usr/lib/oracle/instantclient/instantclient_19_8

# Copiar requirements y proyecto
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponer puerto Flask
EXPOSE 5000

# Comando para arrancar Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
