# --- Etapa 1: Descargador ---
# Esta etapa solo se usa para descargar el dataset de forma segura.
FROM python:3.11-slim AS downloader

# Instalar dependencias
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear el directorio para las credenciales de Kaggle
RUN mkdir -p /root/.kaggle

# Montar el secreto de kaggle.json y ejecutar el script de descarga
# Cloud Build reemplazará esto con el contenido de tu secreto.
COPY utils/kaggle_dataset_download.py ./utils/
RUN --mount=type=secret,id=kaggle_json,target=/root/.kaggle/kaggle.json \
    python -m utils.kaggle_dataset_download

# --- Etapa 2: Imagen Final de Producción ---
# Esta es la imagen que se ejecutará en Cloud Run.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Copiar solo el dataset descargado de la etapa anterior.
# Las credenciales de Kaggle NO se copian aquí.
COPY --from=downloader /app/data_spotify/spotify.sqlite ./data_spotify/spotify.sqlite

# Instalar dependencias y copiar el código de la aplicación
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]