FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libaio1 \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar la carpeta ya descomprimida de Instant Client
COPY instantclient_19_28 /usr/lib/oracle/instantclient/instantclient_19_28

# Configurar variables de entorno para Oracle Instant Client
ENV LD_LIBRARY_PATH=/usr/lib/oracle/instantclient/instantclient_19_28:$LD_LIBRARY_PATH
ENV ORACLE_HOME=/usr/lib/oracle/instantclient/instantclient_19_28

# Copiar requirements y proyecto
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
