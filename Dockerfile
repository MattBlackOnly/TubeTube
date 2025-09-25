FROM python:3.12-alpine

# Install dependencies, including su-exec
RUN apk update && apk add --no-cache ffmpeg su-exec deno

# Create appuser and appgroup
RUN addgroup -g 1000 appgroup && adduser -D -u 1000 -G appgroup appuser

# Set environment variables
ARG TUBETUBE_VERSION
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/tubetube \
    TUBETUBE_VERSION=${TUBETUBE_VERSION}

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip --root-user-action=ignore && \
    pip install --no-cache-dir --root-user-action=ignore -r requirements.txt
    
# Ensure proper ownership of /config, /data and /temp directories
RUN mkdir -p /config /data /temp && \
    chown -R appuser:appgroup /config /data /temp && \
    chmod -R 775 /temp

# Make script executable
RUN chmod +x /app/start.sh

# Expose the application port
EXPOSE 6543

# Use the start script as the entrypoint
ENTRYPOINT ["/app/start.sh"]

