#!/bin/sh

# ASCII Art
echo "-----------------------------------------------------------"
echo "  TTTTT  U   U  BBBBB   EEEEE   TTTTT  U   U  BBBBB   EEEEE"
echo "    T    U   U  B    B  E        T     U   U  B    B  E    "
echo "    T    U   U  BBBBB   EEEE     T     U   U  BBBBB   EEEE "
echo "    T    U   U  B    B  E        T     U   U  B    B  E    "
echo "    T     UUU   BBBBB   EEEEE    T      UUU   BBBBB   EEEEE"
echo "-----------------------------------------------------------"
echo "TUBETUBE - YouTube Downloader using yt-dlp"
echo -e "\e[1;32mDesigned by MattBlackOnly\e[0m" 
echo "-----------------------------------------------------------"

# Log versions
if [ -z "$TUBETUBE_VERSION" ]; then
    echo "TUBETUBE_VERSION environment variable is not set."
else
    echo "Tubetube version: ${TUBETUBE_VERSION}"
fi

if [ -f "requirements.txt" ]; then
    YT_DLP_VERSION=$(awk -F'==' '/yt_dlp\[default\]/{print $2}' requirements.txt)
    if [ -z "$YT_DLP_VERSION" ]; then
        echo "yt-dlp version not found in requirements.txt"
    else
        echo "yt-dlp version: $YT_DLP_VERSION"
    fi
else
    echo "requirements.txt not found."
fi

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

# Ensure ownership of /config, /data and /temp are correct
echo "Setting up directories..."
chown -R appuser:appgroup /config /data /temp

# Start the application as appuser
echo "Starting TubeTube..."
exec su-exec appuser:appgroup gunicorn tubetube.tubetube:app -c start_config.py
