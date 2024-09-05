![Logo](tubetube/static/tubetube.png)


**TubeTube** is a simple YouTube downloader.


## Features:
- **Multithreaded Downloads:** Fast, simultaneous downloads.
- **Custom Locations & Formats:** YAML-based settings.
- **Mobile Optimized:** Designed for small screens.
- **Download Options:** Choose between audio or video.
- **Live Video Support:** Can handle multiple live streams.


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
    environment:
      - THREAD_COUNT=1
      - PUID=1000
      - PGID=1000
    restart: unless-stopped
```


## Folder Configuration

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
  audio_format_id: '625'
Video:
  audio_format_id: '140'
  video_ext: mp4
  video_format_id: '625'

```


### Notes:

- Replace `/path/to/general`, etc.. with actual paths on your host machine.
- Ensure the `settings.yaml` file is correctly placed in the `/path/to/config` directory.
- The volume paths in the `docker-compose.yml` file should match the names specified in the settings.yaml file (e.g., /data/**General**, etc..).
- You can create as many folder locations as needed in `settings.yaml`, but each must be mapped individually in `docker-compose.yml`.
- To use a cookies file, create a `cookies.txt` file and place it in the config directory.


## Screenshot

![Screenshot](tubetube/static/screenshot.png)
