import re
import os
import queue
import logging
import platform
import threading
import random
import yt_dlp
from settings import DownloadCancelledException
import helpers


class DownloadManager:
    def __init__(self):
        self.download_queue = queue.Queue()
        self.all_items = {}
        self.lock = threading.Lock()
        self.stop_signals = {}

        os_system = platform.system()
        logging.info(f"OS: {os_system}")

        self.ffmpeg_location = "D:\\" if os_system == "Windows" else "/usr/bin/ffmpeg"
        logging.info(f"FFmpeg location set to: {self.ffmpeg_location}")

        self.verbose_ytdlp = bool(os.getenv("VERBOSE_LOGS", "False").lower() == "true")
        logging.info(f"Verbose logging for yt-dlp set to: {self.verbose_ytdlp}")

        self.trim_metadata = bool(os.getenv("TRIM_METADATA", "False").lower() == "true")
        logging.info(f"Trim Metadata set to: {self.trim_metadata}")

        self.preferred_language = os.getenv("PREFERRED_LANGUAGE", "en")
        logging.info(f"Preferred Audio Language: {self.preferred_language}")

        self.preferred_audio_codec = os.getenv("PREFERRED_AUDIO_CODEC", "aac")
        logging.info(f"Preferred Audio Codec: {self.preferred_audio_codec}")

        self.preferred_video_codec = os.getenv("PREFERRED_VIDEO_CODEC", "vp9")
        logging.info(f"Preferred Video Codec: {self.preferred_video_codec}")

        self.preferred_video_ext = os.getenv("PREFERRED_VIDEO_EXT", "mp4")
        logging.info(f"Preferred Video Ext: {self.preferred_video_ext}")

        self.embed_subs = bool(os.getenv("EMBED_SUBS", "False").lower() == "true")
        logging.info(f"Embed Subtitles: {self.embed_subs}")

        self.write_subs = bool(os.getenv("WRITE_SUBS", "False").lower() == "true")
        logging.info(f"Write Subtitles: {self.write_subs}")

        self.allow_auto_subs = bool(os.getenv("ALLOW_AUTO_SUBS", "True").lower() == "true")
        logging.info(f"Automatic Subtitles Enabled: {self.allow_auto_subs}")

        self.subtitle_format = os.getenv("SUBTITLE_FORMAT", "vtt")
        logging.info(f"Subtitle Format: {self.subtitle_format}")

        subtitle_langs_env = os.getenv("SUBTITLE_LANGUAGES", "en")
        self.subtitle_languages = [lang.strip() for lang in subtitle_langs_env.split(",") if lang.strip()]
        logging.info(f"Subtitle Languages: {self.subtitle_languages}")

        self.subtitle_config = {
            "subtitlesformat": "best",
            "subtitleslangs": self.subtitle_languages,
            "writeautomaticsub": self.allow_auto_subs,
            "writesubtitles": self.write_subs,
        }
        self.subtitle_pps = []
        if self.write_subs:
            self.subtitle_pps.append({"key": "FFmpegSubtitlesConvertor", "format": self.subtitle_format, "when": "before_dl"})
        if self.embed_subs:
            self.subtitle_pps.append({"key": "FFmpegEmbedSubtitle", "already_have_subtitle": self.write_subs})

        self.thread_count = int(os.getenv("THREAD_COUNT", "4"))
        logging.info(f"Thread Count: {self.thread_count}")

        for i in range(self.thread_count):
            worker = threading.Thread(target=self._process_queue, daemon=True, name=f"Worker-{i}")
            worker.start()
            logging.info(f"Started thread: {worker.name}")

        parsing_opts = {
            "quiet": True,
            "no_color": True,
            "extract_flat": True,
            "ignore_no_formats_error": True,
            "force_generic_extractor": False,
            "cachedir": "/temp/cache",
            "noprogress": True,
            "no_warnings": True,
        }
        self.ydl_for_parsing = yt_dlp.YoutubeDL(parsing_opts)

        self.temp_folder = "/temp"
        self.cleanup_temp_folder()

    def cleanup_temp_folder(self):
        try:
            removable_extensions = (".tmp", ".part", ".webp", ".ytdl", ".png", f".{self.subtitle_format}")
            for file_name in os.listdir(self.temp_folder):
                file_path = os.path.join(self.temp_folder, file_name)
                if os.path.isfile(file_path) and file_name.endswith(removable_extensions):
                    os.remove(file_path)
                    logging.info(f"Deleted file: {file_path}")

        except Exception as e:
            logging.error(f"Error cleaning up temporary folder: {e}")

    def add_to_queue(self, item_info):
        url = item_info.get("url", "")
        logging.info(f"Processing URL: {url}")

        if "&list=" in url:
            url = re.sub(r"&list=.*", "", url)

        with self.lock:
            parsed_identifier = helpers.parse_video_id(url)
            if any(item["url"] == url or item["video_identifier"] == parsed_identifier for item in self.all_items.values()):
                logging.info(f"URL {url} is already in the queue or being downloaded.")
                self.socketio.emit("toast", {"title": "Duplicate URL", "body": f"The video '{url}' is already in the queue or being processed."})
                return

        try:
            yt_info_dict = self.ydl_for_parsing.extract_info(url, download=False)
            logging.info(f"Extracted info for {yt_info_dict.get('title', 'unknown')}")

        except Exception as e:
            logging.error(f"Error extracting info: {e}")
            logging.error(f"Nothing Added to Queue")
            self.socketio.emit("toast", {"title": "Failed to add item to the queue.", "body": f"Please check the URL.\n\n {str(e)}"})
            return

        if "entries" in yt_info_dict:
            playlist_name = re.sub(r'[<>:"/\\|?*]', "-", yt_info_dict.get("title"))
            item_info["folder_name"] = f'{item_info.get("folder_name")}/{playlist_name}'
            logging.info(f"Adding playlist: {playlist_name} to queue")
            for entry in yt_info_dict["entries"]:
                self._enqueue_item(entry, item_info)
        else:
            self._enqueue_item(yt_info_dict, item_info)

    def _enqueue_item(self, yt_info_dict, item_info):
        try:
            download_id = max(self.all_items.keys(), default=-1) + 1
            url = yt_info_dict.get("webpage_url", yt_info_dict.get("url"))
            item = {
                "video_identifier": yt_info_dict.get("id"),
                "id": download_id,
                "title": yt_info_dict.get("title"),
                "url": url,
                "status": "Pending",
                "progress": "0%",
                "folder_name": item_info.get("folder_name"),
                "download_settings": item_info.get("download_settings"),
                "audio_only": item_info.get("audio_only"),
                "skipped": False,
            }
            with self.lock:
                self.all_items[download_id] = item
                self.stop_signals[download_id] = threading.Event()
            self.download_queue.put(download_id)
            logging.info(f'Queued item: {item["title"]} with ID: {download_id}')
            self.socketio.emit("update_download_list", self.all_items)

        except Exception as e:
            logging.error(f"Error enqueuing item: {e}")
            logging.warning(f'Failed to add: {yt_info_dict.get("title")} to the queue.')

        else:
            logging.info(f'Added: {yt_info_dict.get("title")} to queue.')

    def _process_queue(self):
        while True:
            try:
                download_id = self.download_queue.get()
                logging.info(f"Processing download ID: {download_id} in thread {threading.current_thread().name}")

                if self.all_items[download_id]["skipped"]:
                    self.all_items[download_id]["status"] = "Cancelled"
                    logging.info(f"Item {download_id} marked as skipped.")
                    self.socketio.emit("update_download_item", {"item": self.all_items[download_id]})

                else:
                    self._download_item(download_id)

            except Exception as e:
                logging.error(f"Processing error for ID {download_id}: {e}")

            finally:
                self.download_queue.task_done()
                if self.download_queue.empty():
                    logging.info(f"Queue is empty.")

    def _download_item(self, download_id):
        item = self.all_items[download_id]
        item["status"] = "In Progress"
        self.socketio.emit("update_download_item", {"item": item})

        download_settings = item.get("download_settings")
        folder_name = item.get("folder_name")

        video_format_id = download_settings.get("video_format_id", {})
        audio_format_id = download_settings.get("audio_format_id", {})

        if item.get("audio_only"):
            download_format = f"{audio_format_id}/bestaudio/best"
        else:
            download_format = f"{video_format_id}+{audio_format_id}/bestvideo+bestaudio/best"

        item_title = re.sub(r'[<>:"/\\|?*]', "-", item.get("title"))
        final_path = f"/data/{folder_name}"

        ydl_opts = {
            "ignore_no_formats_error": True,
            "noplaylist": True,
            "outtmpl": f"{item_title}_%(upload_date)s.%(ext)s",
            "progress_hooks": [lambda d: self._progress_hook(d, download_id)],
            "ffmpeg_location": self.ffmpeg_location,
            "writethumbnail": True,
            "quiet": not self.verbose_ytdlp,
            "extract_flat": True,
            "format": download_format,
            "updatetime": False,
            "live_from_start": True,
            "extractor_args": {"youtubetab": {"skip": ["authcheck"]}},
            "paths": {"home": final_path, "temp": self.temp_folder},
            "no_overwrites": True,
            "verbose": self.verbose_ytdlp,
            "no_mtime": True,
            "format_sort": [f"lang:{self.preferred_language}", f"acodec:{self.preferred_audio_codec}", "quality", "size", f"vcodec:{self.preferred_video_codec}", f"vext:{self.preferred_video_ext}"],
        }

        post_processors = [
            {"key": "SponsorBlock", "categories": ["sponsor"]},
            {"key": "ModifyChapters", "remove_sponsor_segments": ["sponsor"]},
        ]

        if item.get("audio_only"):
            audio_ext = download_settings.get("audio_ext", "m4a")
            post_processors.extend([{"key": "FFmpegExtractAudio", "preferredcodec": audio_ext, "preferredquality": "0"}])

        post_processors.append({"key": "FFmpegThumbnailsConvertor", "format": "png", "when": "before_dl"})
        post_processors.append({"key": "EmbedThumbnail"})
        post_processors.append({"key": "FFmpegMetadata"})

        if not item.get("audio_only"):
            ydl_opts["merge_output_format"] = "mp4"

        if self.cookies_file:
            ydl_opts["cookiefile"] = self.cookies_file

        if self.write_subs or self.embed_subs:
            ydl_opts.update(self.subtitle_config)
            post_processors.extend(self.subtitle_pps)

        ydl_opts["postprocessors"] = post_processors

        try:
            logging.info(f'Starting {threading.current_thread().name} Download: {item.get("title")}')
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            if self.trim_metadata:
                ydl.add_post_processor(helpers.TrimDescriptionPP(), when="before_dl")
            result = ydl.download([item["url"]])
            item["progress"] = "Done" if result == 0 else "Incomplete"
            item["status"] = "Complete"
            logging.info(f'Finished {threading.current_thread().name} Download: {item.get("title")}')

        except DownloadCancelledException:
            item["status"] = "Cancelled"
            logging.info(f'Download cancelled: {item.get("title")}')

        except Exception as e:
            item["status"] = f"Failed: {type(e).__name__}"
            item["progress"] = "Error"
            logging.error(f'Error downloading: {item.get("title")} - {str(e)}')

        finally:
            self.socketio.emit("update_download_item", {"item": item})
            ydl.close()

    def _progress_hook(self, d, download_id):
        if self.stop_signals[download_id].is_set():
            raise DownloadCancelledException("Cancelled")

        if d["status"] == "downloading":
            if random.randint(1, 10) != 1:
                return

            with self.lock:
                item = self.all_items[download_id]
                live = d.get("info_dict", {}).get("is_live", False)
                if live:
                    fragment_index_str = d.get("fragment_index", 1)
                    elapsed_str = re.sub(r"\x1b\[[0-9;]*m", "", d.get("_elapsed_str", "")).strip()
                    progress_message = f"Frag: {fragment_index_str} ({elapsed_str})"
                else:
                    percent_str = re.sub(r"\x1b\[[0-9;]*m", "", d.get("_percent_str", "")).strip()
                    speed_str = re.sub(r"\x1b\[[0-9;]*m", "", d.get("_speed_str", "")).strip()
                    progress_message = f"{percent_str} at {speed_str}"

                item["progress"] = progress_message
                item["status"] = "Downloading"
                self.socketio.emit("update_download_item", {"item": item})

        elif d["status"] == "finished":
            with self.lock:
                item = self.all_items[download_id]
                item["progress"] = "Downloaded"
                item["status"] = "Processing"
                logging.info(f'Download finished: {item.get("title")} - processing now')
                self.socketio.emit("update_download_item", {"item": item})

    def cancel_items(self, item_ids):
        with self.lock:
            for item_id in item_ids:
                if item_id in self.all_items:
                    self.all_items[item_id]["skipped"] = True
                    self.all_items[item_id]["status"] = "Cancelling"
                    logging.info(f"Item {item_id} marked for cancellation.")
                    if item_id in self.stop_signals:
                        self.stop_signals[item_id].set()
                    self.socketio.emit("update_download_item", {"item": self.all_items[item_id]})

    def remove_items(self, item_ids):
        with self.lock:
            for item_id in item_ids:
                if item_id in self.all_items:
                    logging.info(f"Removing item {item_id}")
                    if item_id in self.stop_signals:
                        self.stop_signals[item_id].set()
                    del self.all_items[item_id]
                    if item_id in self.stop_signals:
                        del self.stop_signals[item_id]
                    self.socketio.emit("remove_download_item", {"id": item_id})
