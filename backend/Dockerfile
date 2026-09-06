# Imagen base ligera de Python
FROM python:3.10-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar e instalar dependencias
COPY requisitos.txt .
RUN pip install --no-cache-dir -r requisitos.txt

# Copiar el resto del código del proyecto
COPY . .

# Comando por defecto para ejecutar la aplicación
CMD ["python", "backend/main.py"]
