FROM python:3.11-slim

WORKDIR /app

# Instalar libGL.so.1 para OpenCV
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Eliminar cualquier venv previo
RUN rm -rf .venv

# Crear entorno virtual
RUN python -m venv .venv
RUN .venv/bin/pip install --upgrade pip

# Copiar dependencias e instalarlas
COPY requirements.txt ./
RUN .venv/bin/pip install -r requirements.txt

# Verificar uvicorn instalado (opcional)
RUN .venv/bin/pip show uvicorn || (echo "❌ uvicorn no instalado" && exit 1)

# Copiar el resto del código
COPY . .

# Ejecutar la app
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
