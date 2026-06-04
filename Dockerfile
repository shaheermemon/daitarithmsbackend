FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (faster build)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]