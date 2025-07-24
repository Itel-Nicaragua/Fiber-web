FROM python:3.11-slim

WORKDIR /app

# Instalar herramientas necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libaio1 \
    unixodbc-dev \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear el directorio destino de Oracle
RUN mkdir -p /usr/lib/oracle

# Copiar los archivos ZIP al contenedor
COPY instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip /tmp/
COPY instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip /tmp/

# Extraer los paquetes
RUN unzip /tmp/instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip -d /usr/lib/oracle/ && \
    unzip /tmp/instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip -d /usr/lib/oracle/ && \
    rm /tmp/instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip /tmp/instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip

# Crear symlink para simplificar el path
RUN ln -s /usr/lib/oracle/instantclient_19_28 /usr/lib/oracle/instantclient

# Variables de entorno para Oracle Instant Client
ENV LD_LIBRARY_PATH=/usr/lib/oracle/instantclient
ENV ORACLE_HOME=/usr/lib/oracle/instantclient

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
