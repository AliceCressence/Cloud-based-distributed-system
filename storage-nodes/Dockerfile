FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directory for virtual disks
RUN mkdir -p /app/vdisks

# Expose gRPC port (will be overridden by specific node)
EXPOSE 50051

CMD ["python", "node.py"]
