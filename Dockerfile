FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para cx_Oracle, pyodbc y el driver ODBC SQL Server
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libaio1 \
    unixodbc-dev \
    curl \
    gnupg2 \
    apt-transport-https \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Agregar repositorio Microsoft para instalar ODBC Driver 17
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Crear carpeta para Oracle Instant Client e instalarlo copiando los zips locales
RUN mkdir -p /usr/lib/oracle/

COPY instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip /tmp/
COPY instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip /tmp/

RUN unzip /tmp/instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip -d /usr/lib/oracle/instantclient_19_28 && \
    unzip /tmp/instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip -d /usr/lib/oracle/instantclient_19_28 && \
    rm /tmp/instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip /tmp/instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip

# Configurar variables de entorno para Oracle Instant Client
ENV LD_LIBRARY_PATH=/usr/lib/oracle/instantclient_19_28:$LD_LIBRARY_PATH
ENV ORACLE_HOME=/usr/lib/oracle/instantclient_19_28

# Copiar requirements.txt e instalar dependencias Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto de Flask
EXPOSE 5000

# Comando para arrancar Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
