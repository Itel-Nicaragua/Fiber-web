FROM python:3.11-slim

WORKDIR /app

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

# Importar la clave pública de Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
    install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/ && \
    rm microsoft.gpg

# Agregar el repositorio Microsoft para Debian 12 (bookworm)
RUN curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Crear carpeta para Oracle Instant Client e instalarlo copiando los zips locales
RUN mkdir -p /usr/lib/oracle/

COPY instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip /tmp/
COPY instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip /tmp/

RUN unzip /tmp/instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip -d /usr/lib/oracle/instantclient_19_28 && \
    unzip /tmp/instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip -d /usr/lib/oracle/instantclient_19_28 && \
    rm /tmp/instantclient-basiclite-linux.x64-19.28.0.0.0dbru.zip /tmp/instantclient-sdk-linux.x64-19.28.0.0.0dbru.zip

ENV LD_LIBRARY_PATH=/usr/lib/oracle/instantclient_19_28:$LD_LIBRARY_PATH
ENV ORACLE_HOME=/usr/lib/oracle/instantclient_19_28

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
