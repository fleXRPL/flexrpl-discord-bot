FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a start script
RUN echo '#!/bin/bash\nuvicorn app:app --host 0.0.0.0 --port "${PORT:-8000}"' > start.sh && \
    chmod +x start.sh

# Use the start script
CMD ["./start.sh"]