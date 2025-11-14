FROM python:3.11-slim
WORKDIR /app

# Copy only backend, not whole project
COPY backend/ /app/

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Render uses $PORT)
EXPOSE 8000

# Start FastAPI
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]
