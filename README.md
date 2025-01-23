![Logo](tubetube/static/tubetube.png)


**TubeTube** is a simple YouTube downloader.


## Features:
- **Multithreaded Downloads:** Fast, simultaneous downloads.
- **Custom Locations & Formats:** YAML-based settings.
- **Mobile Optimized:** Designed for small screens.
- **Download Options:** Choose between audio or video.
- **Live Video Support:** Supports multiple live streams.


## Docker Compose Configuration

Create a `docker-compose.yml` file:

```yaml
services:
  tubetube:
    image: ghcr.io/mattblackonly/tubetube:latest
    container_name: tubetube
    ports:
      - 6543:6543
    volumes:
      - /path/to/general:/data/General
      - /path/to/music:/data/Music
      - /path/to/podcasts:/data/Podcast
      - /path/to/videos:/data/Video
      - /path/to/config:/config
      - /path/to/temp:/temp # Optional. Temp files are deleted on startup.
      - /etc/localtime:/etc/localtime:ro # Optional. Sync time with host.
      - /etc/timezone:/etc/timezone:ro # Optional. Sync timezone with host.
    environment:
      - PUID=1000
      - PGID=1000
    restart: unless-stopped
```


## Directory Configuration

Create a `settings.yaml` file in the `/path/to/config` directory with the following format:

```yaml
General:
  audio_ext: m4a
  audio_format_id: '140'
  video_ext: mp4
  video_format_id: '625'
Music:
  audio_ext: mp3
  audio_format_id: '140'
Podcast:
  audio_ext: m4a
  audio_format_id: '140'
Video:
  audio_format_id: '140'
  video_ext: mp4
  video_format_id: '625'

```


### Notes:

- Replace `/path/to/general`, etc.. with actual paths on your host machine.
- Ensure the `settings.yaml` file is correctly placed in the `/path/to/config` directory.
- The volume paths in the `docker-compose.yml` file should match the names specified in the settings.yaml file (e.g., /data/**General**, etc..).
- You can create as many directory locations as needed in `settings.yaml`, but each must be mapped individually in `docker-compose.yml`.
- To use a cookies file, create a `cookies.txt` file and place it in the config directory.

#### Subtitle Configuration

- When `WRITE_SUBS=True`, actual subtitles will be saved to a subtitle file. If no actual subtitles are available, no subtitles will be created. Additionally, setting `ALLOW_AUTO_SUBS=True` provides a fallback to automatically generated subtitles saved to the subtitle file.
- When `EMBED_SUBS=True`, actual subtitles will be embedded into the video. If no actual subtitles are present, no subtitles will be included. Similarly, `ALLOW_AUTO_SUBS=True` can serve as a fallback to embed automatically generated subtitles.

To effectively manage subtitles, enable `ALLOW_AUTO_SUBS` in conjunction with either `WRITE_SUBS` or `EMBED_SUBS`. This configuration will attempt to download actual subtitles, and if they are not available, it will default to using automatically generated subtitles.

## Configuration via Environment Variables

Customize the behavior of **TubeTube** by setting the following environment variables in your `docker-compose.yml` file:

```yaml
environment:
  - PUID=1000                       # User ID for permissions (default: 1000)
  - PGID=1000                       # Group ID for permissions (default: 1000)
  - VERBOSE_LOGS=false              # Enable verbose logging for yt-dlp (default: false)
  - TRIM_METADATA=false             # Trim metadata from files (default: false)
  - PREFERRED_LANGUAGE=en           # Desired audio language for downloads (default: en)
  - PREFERRED_AUDIO_CODEC=aac       # Desired audio codec (default: aac)
  - PREFERRED_VIDEO_CODEC=vp9       # Desired video codec (default: vp9)
  - PREFERRED_VIDEO_EXT=mp4         # Desired video file extension (default: mp4)
  - EMBED_SUBS=false                # Embed subtitles in the video (default: false)
  - WRITE_SUBS=false                # Write subtitles as separate files (default: false)
  - ALLOW_AUTO_SUBS=false           # Allow automatically generated subtitles as a fallback (default: true)
  - SUBTITLE_FORMAT=vtt             # Format of the subtitles (default: vtt)
  - SUBTITLE_LANGUAGES=en           # Subtitle language (default: en)
  - THREAD_COUNT=4                  # Number of threads for processing (default: 4)
```

## Screenshots

### Phone (Dark Mode)

![Phone](tubetube/static/phone-screenshot.png)



### Desktop (Dark Mode)

![Screenshot](tubetube/static/screenshot.png)


## Star History

<a href="https://star-history.com/#mattblackonly/tubetube&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=mattblackonly/tubetube&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=mattblackonly/tubetube&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=mattblackonly/tubetube&type=Date" />
 </picture>
</a>