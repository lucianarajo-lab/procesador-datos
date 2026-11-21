# Imagen base ligera con versión fija (no "latest")
FROM python:3.12.7-slim-bookworm

# Variables de entorno por defecto (se pueden cambiar al ejecutar con -e)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    INPUT_PATH=/data/input/ventas.csv \
    OUTPUT_DIR=/data/output

WORKDIR /app

# 1) Primero solo requirements.txt: si no cambia, Docker reutiliza la caché
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Usuario sin privilegios y carpetas de datos
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /data/input /data/output \
    && chown -R appuser:appuser /data

# 3) Después el código (cambia más seguido, por eso va al final)
COPY --chown=appuser:appuser procesar_datos.py .

USER appuser

# CMD en forma exec (lista JSON)
CMD ["python", "procesar_datos.py"]
