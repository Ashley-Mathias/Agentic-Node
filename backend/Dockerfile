FROM python:3.11-slim

WORKDIR /app

# Install system deps for psycopg2 and matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway injects PORT=8080 at runtime; app must listen on this port
EXPOSE 8080
CMD ["python", "-m", "run"]
