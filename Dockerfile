FROM python:3.12-alpine

# Install dependencies, including su-exec
RUN apk update && apk add --no-cache ffmpeg su-exec

# Create appuser and appgroup
RUN addgroup -g 1000 appgroup && adduser -D -u 1000 -G appgroup appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/tubetube

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Ensure proper ownership of /config and /data directories
RUN mkdir -p /config /data /temp && chown -R appuser:appgroup /config /data /temp

# Copy start script and make it executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose the application port
EXPOSE 6543

# Use the start script as the entrypoint
ENTRYPOINT ["/app/start.sh"]
