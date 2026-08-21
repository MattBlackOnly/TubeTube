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
        echo "yt-dlp requirements.txt version: $YT_DLP_VERSION"
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

# yt-dlp auto-update via cron
# YTDLP_UPDATE: "latest" or "nightly" — omit or leave blank to disable
# YTDLP_UPDATE_HOUR: 0-23 (default: 3)
if [ -n "$YTDLP_UPDATE" ]; then
    YTDLP_UPDATE_HOUR=${YTDLP_UPDATE_HOUR:-3}

    # Validate update hour
    case "$YTDLP_UPDATE_HOUR" in
        ''|*[!0-9]*)
            echo "Invalid YTDLP_UPDATE_HOUR: ${YTDLP_UPDATE_HOUR}"
            echo "YTDLP_UPDATE_HOUR must be between 0 and 23."
            exit 1
            ;;
    esac

    if [ "$YTDLP_UPDATE_HOUR" -gt 23 ]; then
        echo "Invalid YTDLP_UPDATE_HOUR: ${YTDLP_UPDATE_HOUR}"
        echo "YTDLP_UPDATE_HOUR must be between 0 and 23."
        exit 1
    fi

    case "$YTDLP_UPDATE" in
        nightly)
            YTDLP_PRE_FLAG="--pre"
            ;;
        latest)
            YTDLP_PRE_FLAG=""
            ;;
        *)
            echo "Invalid YTDLP_UPDATE value: $YTDLP_UPDATE"
            echo "Valid values are: latest or nightly"
            exit 1
            ;;
    esac

    echo "yt-dlp auto-update enabled: ${YTDLP_UPDATE} at hour ${YTDLP_UPDATE_HOUR}"

    echo "0 ${YTDLP_UPDATE_HOUR} * * * python -m pip install --upgrade ${YTDLP_PRE_FLAG} yt-dlp\[default\] --quiet --break-system-packages >> /config/ytdlp-update.log 2>&1" \
        > /var/spool/cron/crontabs/root

    chmod 600 /var/spool/cron/crontabs/root

    crond -b -l 8
    echo "crond started."
else
    echo "yt-dlp auto-update disabled."
fi

# Start the application as appuser
echo "Starting TubeTube..."
exec su-exec appuser:appgroup gunicorn tubetube.tubetube:app -c start_config.py
