# Imagen base de Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY requirements.txt ./
COPY . .

# Instalar paquetes del sistema necesarios para pyodbc y otros
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar las carpetas necesarias del frontend (si no estaban copiadas antes)
COPY templates/ templates/
COPY static/ static/

# Exponer el puerto del servidor Flask
EXPOSE 5000

# Comando de ejecución
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
