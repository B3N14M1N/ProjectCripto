# Dockerfile pentru SecureChat
# Aplicatie de chat cu criptare end-to-end AES+RSA
# Multi-stage build pentru productie

# Stage 1: Build React frontend
FROM node:18-slim AS frontend-builder

WORKDIR /web
COPY web/package*.json ./
RUN npm install
COPY web/ .
RUN npm run build

# Stage 2: Python backend + frontend static files
FROM python:3.9-slim

WORKDIR /app

# Copiem si instalam dependintele Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiem codul backend
COPY app/ ./app/

# Copiem frontend-ul build-uit
COPY --from=frontend-builder /web/build ./web/build

# Cream directorul pentru date (SQLite + uploads)
RUN mkdir -p /app/data/uploads

# Expunem portul
EXPOSE 5000

# Setam variabile de mediu
ENV FLASK_APP=app/app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Pornim aplicatia
WORKDIR /app/app
CMD ["python", "app.py"]
