import re
import os
import queue
import logging
import platform
import threading
import yt_dlp
from settings import DownloadCancelledException


class DownloadManager:
    def __init__(self):
        self.download_queue = queue.Queue()
        self.all_items = {}
        self.lock = threading.Lock()
        self.stop_signals = {}
        self.thread_count = int(os.getenv("THREAD_COUNT", "4"))
        logging.info(f"{self.thread_count = }")

        os_system = platform.system()
        logging.info(f"{os_system = }")

        if os_system == "Windows":
            self.ffmpeg_location = "D:\\"
        else:
            self.ffmpeg_location = "/usr/bin/ffmpeg"

        for i in range(self.thread_count):
            worker = threading.Thread(target=self._process_queue, daemon=True, name=f"Worker-{i}")
            worker.start()

        parsing_opts = {
            "quiet": True,
            "no_color": True,
            "extract_flat": True,
            "ignore_no_formats_error": True,
            "force_generic_extractor": False,
            "cachedir": True,
            "noprogress": True,
            "no_warnings": True,
        }
        self.ydl_for_parsing = yt_dlp.YoutubeDL(parsing_opts)

    def add_to_queue(self, item_info):
        url = item_info.get("url", "")
        try:
            yt_info_dict = self.ydl_for_parsing.extract_info(url, download=False)

        except Exception as e:
            logging.error(f"Error extracting info: {e}")
            logging.error(f"Nothing Added to Queue")
            return

        if "entries" in yt_info_dict:
            item_info["folder_name"] = f'{item_info.get("folder_name")}/{yt_info_dict.get("title")}'
            for entry in yt_info_dict["entries"]:
                self._enqueue_item(entry, item_info)
        else:
            self._enqueue_item(yt_info_dict, item_info)

    def _enqueue_item(self, yt_info_dict, item_info):
        try:
            download_id = max(self.all_items.keys(), default=-1) + 1
            url = yt_info_dict.get("webpage_url", yt_info_dict.get("url"))
            item = {
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

                if self.all_items[download_id]["skipped"]:
                    self.all_items[download_id]["status"] = "Cancelled"
                    self.socketio.emit("update_download_item", {"item": self.all_items[download_id]})

                else:
                    self._download_item(download_id)

            except Exception as e:
                logging.error(f"Processing Error: {e}")

            finally:
                self.download_queue.task_done()
                if self.download_queue.empty():
                    logging.info(f"Queue Empty")

    def _download_item(self, download_id):
        item = self.all_items[download_id]
        item["status"] = "In Progress"
        self.socketio.emit("update_download_item", {"item": item})

        download_settings = item.get("download_settings")
        folder_name = item.get("folder_name")

        video_format_id = download_settings.get("video_format_id", {})
        audio_format_id = download_settings.get("audio_format_id", {})

        if item.get("audio_only", False):
            download_format = f"{audio_format_id}/bestaudio/best"
        else:
            download_format = f"{video_format_id}+{audio_format_id}/bestvideo+bestaudio/best"

        ydl_opts = {
            "ignore_no_formats_error": True,
            "noplaylist": True,
            "outtmpl": f"/data/{folder_name}/%(title)s.%(ext)s",
            "progress_hooks": [lambda d: self._progress_hook(d, download_id)],
            "ffmpeg_location": self.ffmpeg_location,
            "writethumbnail": True,
            "quiet": True,
            "extract_flat": True,
            "format": download_format,
            "no_mtime": True,
            "live_from_start": True,
            "extractor_args": {"youtubetab": {"skip": ["authcheck"]}},
        }
        post_processors = [
            {"key": "EmbedThumbnail"},
            {"key": "FFmpegMetadata"},
        ]
        if item.get("audio_only", False):
            post_processors.append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": download_settings.get("audio_ext", "m4a"),
                    "preferredquality": "192",
                }
            )
        else:
            ydl_opts["merge_output_format"] = "mp4"

        if self.cookies_file:
            ydl_opts["cookiefile"] = self.cookies_file

        ydl_opts["postprocessors"] = post_processors

        try:
            logging.info(f'Starting Download: {item.get("title")}')
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            ydl.download([item["url"]])
            item["status"] = "Complete"
            logging.info(f'Finished Download: {item.get("title")}')

        except DownloadCancelledException:
            item["status"] = "Cancelled"

        except Exception as e:
            item["status"] = f"Failed: {type(e).__name__}"
            item["progress"] = "Error"
            logging.error(f'Error downloading: {item.get("title")} - {str(e)}')

        finally:
            self.socketio.emit("update_download_item", {"item": item})

    def _progress_hook(self, d, download_id):
        if self.stop_signals[download_id].is_set():
            raise DownloadCancelledException("Cancelled")

        if d["status"] == "downloading":
            with self.lock:
                item = self.all_items[download_id]
                live = d.get("info_dict", {}).get("is_live", False)
                if live:
                    fragment_index_str = d.get("fragment_index", 1)
                    elapsed_str = re.sub(r"\x1b\[[0-9;]*m", "", d.get("_elapsed_str", "")).strip()
                    progress_message = f"{fragment_index_str} ({elapsed_str})"
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
                item["progress"] = "Done"
                item["status"] = "Processing"
                self.socketio.emit("update_download_item", {"item": item})

    def cancel_items(self, item_ids):
        with self.lock:
            for item_id in item_ids:
                if item_id in self.all_items:
                    self.all_items[item_id]["skipped"] = True
                    self.all_items[item_id]["status"] = "Cancelling"
                    if item_id in self.stop_signals:
                        self.stop_signals[item_id].set()
                    self.socketio.emit("update_download_item", {"item": self.all_items[item_id]})

    def remove_items(self, item_ids):
        with self.lock:
            for item_id in item_ids:
                if item_id in self.all_items:
                    if item_id in self.stop_signals:
                        self.stop_signals[item_id].set()
                    del self.all_items[item_id]
                    if item_id in self.stop_signals:
                        del self.stop_signals[item_id]
                    self.socketio.emit("remove_download_item", {"id": item_id})
