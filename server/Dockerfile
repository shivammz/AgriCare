# Use slim Python base
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /server

# Copy entire local server folder into container's /server
COPY . /server

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run uvicorn from / (container root), target server.main
WORKDIR /

# Run FastAPI
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8080"]
