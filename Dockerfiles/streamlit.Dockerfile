# app/Dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY .env ./.env
COPY src/config/api_keys.py ./src/config/api_keys.py  
COPY .streamlit/secrets.toml .streamlit/
COPY app.py ./app.py

RUN pip install --no-cache-dir SQLAlchemy pandas requests streamlit python-dotenv psycopg2-binary

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Separar cada parte del comando en una lista
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
