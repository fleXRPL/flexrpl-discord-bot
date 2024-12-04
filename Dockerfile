FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY config.py .

ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000

CMD ["uvicorn", "app:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--no-access-log", \
     "--limit-concurrency", "100", \
     "--timeout-keep-alive", "5"]