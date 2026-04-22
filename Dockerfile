FROM python:3.11-slim

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY . .

# Porta padrão Railway
EXPOSE 8000

# Inicia com gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
