FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para cx_Oracle y pyodbc
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libaio1 \
    unixodbc-dev \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar Oracle Instant Client básico y SDK
RUN curl -L -o instantclient-basiclite.zip https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linux.x64-19.8.0.0.0dbru.zip \
    && curl -L -o instantclient-sdk.zip https://download.oracle.com/otn_software/linux/instantclient/instantclient-sdk-linux.x64-19.8.0.0.0dbru.zip \
    && unzip instantclient-basiclite.zip -d /usr/lib/oracle/instantclient \
    && unzip instantclient-sdk.zip -d /usr/lib/oracle/instantclient \
    && rm instantclient-basiclite.zip instantclient-sdk.zip

ENV LD_LIBRARY_PATH=/usr/lib/oracle/instantclient/instantclient_19_8:$LD_LIBRARY_PATH
ENV ORACLE_HOME=/usr/lib/oracle/instantclient/instantclient_19_8

# Copiar archivos del proyecto
COPY requirements.txt ./
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto 5000 para Flask
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
