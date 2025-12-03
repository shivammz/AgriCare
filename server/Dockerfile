# Use slim Python base
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy entire local server folder into container's /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run FastAPI from /app (the server directory)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
