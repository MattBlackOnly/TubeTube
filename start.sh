#!/bin/sh

# Default values for PUID and PGID
PUID=${PUID:-1000}
PGID=${PGID:-1000}
echo "Using PUID=${PUID} and PGID=${PGID}"

# Change ownership of the directories to match PUID and PGID
mkdir -p /config
mkdir -p /data
chown -R ${PUID}:${PGID} /config
chown -R ${PUID}:${PGID} /data

# Start TubeTube
echo "Starting TubeTube Gunicorn server..."
exec gunicorn tubetube.tubetube:app -c gunicorn_setup.py
