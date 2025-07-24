# Etapa 1: Build frontend (Tailwind + Flowbite)
FROM node:18 AS frontend

WORKDIR /app

# Copiamos package.json y package-lock.json para instalar dependencias Node
COPY package.json package-lock.json* ./
RUN npm install

# Copiamos la config de Tailwind y el input.css
COPY tailwind.config.js ./static/src/input.css ./static/src/

# Ejecutamos el build del CSS
RUN npm run build:css

# Etapa 2: Backend Flask
FROM python:3.11-slim AS backend

WORKDIR /app

# Copiamos todo el código
COPY . .

# Copiamos el CSS compilado desde la etapa frontend
COPY --from=frontend /app/static/dist/output.css ./static/dist/output.css

# Instalamos dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponemos el puerto 5000 para Flask
EXPOSE 5000

# Ejecutamos la app Flask, escuchando en todas las interfaces
CMD ["flask", "run", "--host=0.0.0.0"]
