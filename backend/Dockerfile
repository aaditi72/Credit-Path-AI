# -------------------------------------------------------
# 1️⃣ Base Image (Slim + Python 3.11)
# -------------------------------------------------------
FROM python:3.11-slim

# Prevent interactive prompts
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -------------------------------------------------------
# 2️⃣ Install system dependencies
# -------------------------------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------
# 3️⃣ Set working directory
# -------------------------------------------------------
WORKDIR /app

# -------------------------------------------------------
# 4️⃣ Copy requirements first (for caching)
# -------------------------------------------------------
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------
# 5️⃣ Copy entire project (backend, models, etc.)
# -------------------------------------------------------
COPY . /app/

# -------------------------------------------------------
# 6️⃣ Expose Render port (Render sets $PORT)
# -------------------------------------------------------
EXPOSE 10000

# -------------------------------------------------------
# 7️⃣ Start FastAPI with UVicorn
# -------------------------------------------------------
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]
