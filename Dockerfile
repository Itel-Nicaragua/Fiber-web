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

# Copiar los archivos del Instant Client (versión 19.28)
COPY instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip /tmp/
COPY instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip /tmp/

# Descomprimir Oracle Instant Client (asegurando que exista el directorio)
RUN mkdir -p /usr/lib/oracle/instantclient && \
    unzip /tmp/instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip -d /usr/lib/oracle/instantclient && \
    unzip /tmp/instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip -d /usr/lib/oracle/instantclient && \
    rm /tmp/instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip /tmp/instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip
    
# Establecer variables de entorno para Oracle Instant Client (ajustar según nombre de carpeta)
ENV LD_LIBRARY_PATH=/usr/lib/oracle/instantclient/instantclient_19_28:$LD_LIBRARY_PATH
ENV ORACLE_HOME=/usr/lib/oracle/instantclient/instantclient_19_28

# Copiar requirements.txt e instalar dependencias Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer el puerto para Flask
EXPOSE 5000

# Comando para iniciar la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
