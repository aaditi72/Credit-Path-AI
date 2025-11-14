# Dockerfile at repo root
FROM python:3.11-slim

WORKDIR /app

# Install system packages required by LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy backend folder into container
COPY backend/ /app/

# Install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]
