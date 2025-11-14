FROM python:3.11-slim

WORKDIR /app

# Copy everything in backend folder INTO the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]
