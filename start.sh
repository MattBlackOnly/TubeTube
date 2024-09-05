#!/bin/sh

# Default values for PUID and PGID
PUID=${PUID:-1000}
PGID=${PGID:-1000}

echo "Using PUID=${PUID} and PGID=${PGID}"

# Modify the appuser and appgroup to match PUID and PGID
if [ "$(id -u appuser)" != "$PUID" ] || [ "$(id -g appuser)" != "$PGID" ]; then
    echo "Updating UID and GID for appuser to match PUID:PGID..."
    deluser appuser
    addgroup -g "$PGID" appgroup
    adduser -D -u "$PUID" -G appgroup appuser
fi

# Ensure ownership of /config and /data is correct
chown -R appuser:appgroup /config /data

# Start the application as appuser
exec su-exec appuser:appgroup gunicorn tubetube.tubetube:app -c gunicorn_setup.py
