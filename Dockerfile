# Etapa 1: Construcción CSS con Node y Tailwind
FROM node:18 AS frontend

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY tailwind.config.js ./static/src/input.css ./static/src/
RUN npm run build:css

# Etapa 2: Backend Python Flask
FROM python:3.11-slim AS backend

WORKDIR /app

COPY . .

# Copiamos el CSS ya compilado desde la etapa frontend
COPY --from=frontend /app/static/css/output.css ./static/css/output.css

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
