FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-c", "import os; from uvicorn.main import run; run('app:app', host='0.0.0.0', port=int(os.getenv('PORT', '8000')))"]