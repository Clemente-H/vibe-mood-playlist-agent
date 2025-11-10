# --- Etapa 1: Descargador ---
# Esta etapa solo se usa para descargar el dataset de forma segura.
FROM python:3.11-slim AS downloader

# Instalar dependencias
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear el directorio para las credenciales de Kaggle
RUN mkdir -p /root/.kaggle

# Copiar el script de descarga
COPY utils/kaggle_dataset_download.py ./utils/

# Este ARG se pasará durante el build desde Cloud Build
ARG KAGGLE_JSON_CONTENT=""

# Descargar dataset usando credentials
RUN if [ -n "$KAGGLE_JSON_CONTENT" ]; then \
        echo "$KAGGLE_JSON_CONTENT" > /root/.kaggle/kaggle.json && \
        chmod 600 /root/.kaggle/kaggle.json && \
        python -m utils.kaggle_dataset_download && \
        rm -f /root/.kaggle/kaggle.json; \
    else \
        echo "WARNING: KAGGLE_JSON_CONTENT not provided, skipping dataset download"; \
    fi

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