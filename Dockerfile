FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY app.py .
COPY config.py .

ENV PYTHONPATH=/app

CMD ["python", "src/main.py"]
