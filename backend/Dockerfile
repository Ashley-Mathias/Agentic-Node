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

# Railway Networking is often set to 8000 in Settings; app listens on PORT (default 8000)
EXPOSE 8000
CMD ["python", "-m", "run"]
