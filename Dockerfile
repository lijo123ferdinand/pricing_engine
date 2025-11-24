# Dockerfile for pricing_engine
FROM python:3.12-slim

WORKDIR /app

# system deps (if needed)
RUN apt-get update && apt-get install -y build-essential default-libmysqlclient-dev gcc

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app
COPY . /app

ENV PYTHONUNBUFFERED=1
ENV MODEL_DIR=/app/models_artifacts

EXPOSE 8000

CMD ["python", "app.py"]
