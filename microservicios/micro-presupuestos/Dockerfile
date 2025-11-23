FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias del sistema (para que pip funcione bien) + curl para healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copiamos requirements
COPY requirements.txt .

RUN pip install -r requirements.txt

# Copiamos el código
COPY . .

EXPOSE 5001

# Comando: gunicorn apuntando al objeto app del archivo ppto.py
CMD ["gunicorn", "-b", "0.0.0.0:5001", "ppto:app"]
