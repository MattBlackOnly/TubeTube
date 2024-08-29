#!/bin/sh
# Start TubeTube
echo "Starting TubeTube Gunicorn server..."
# Start the Gunicorn server
exec gunicorn tubetube.tubetube:app -c gunicorn_setup.py
