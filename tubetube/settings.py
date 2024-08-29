import os
import logging
import yaml


class DownloadCancelledException(Exception):
    pass


class Config:
    SECRET_KEY = "a_secret_key"
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    DEFAULT_FOLDER_LOCATIONS = {
        "Video": {"video_ext": "mp4", "video_format_id": "625", "audio_format_id": "140"},
        "Music": {"audio_ext": "mp3", "audio_format_id": "140"},
        "Podcast": {"audio_ext": "m4a", "audio_format_id": "625"},
        "General": {"audio_ext": "m4a", "audio_format_id": "140", "video_ext": "mp4", "video_format_id": "625"},
    }


class Settings:
    def __init__(self):
        self.file_path = "settings.yaml"
        self.folder_locations = self._load_settings()
        self.audio_locations, self.video_locations = self._categorise_locations()

        all_folders = set(self.audio_locations.keys()).union(set(self.video_locations.keys()))

        for folder_name in all_folders:
            os.makedirs(os.path.join("/data", folder_name), exist_ok=True)

        os.makedirs("config", exist_ok=True)

        cookies_json_file = os.path.join("config", "cookies.txt")
        self.cookies_file = cookies_json_file if os.path.exists(cookies_json_file) else None

    def _load_settings(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                yaml.safe_dump(Config.DEFAULT_FOLDER_LOCATIONS, file, default_flow_style=False)
            return Config.DEFAULT_FOLDER_LOCATIONS

        try:
            with open(self.file_path, "r") as file:
                return yaml.safe_load(file) or Config.DEFAULT_FOLDER_LOCATIONS

        except yaml.YAMLError as e:
            logging.error(f"YAML loading error: {e}")
            return Config.DEFAULT_FOLDER_LOCATIONS

    def _categorise_locations(self):
        audio_locations = {}
        video_locations = {}

        for folder_name, download_settings in self.folder_locations.items():
            has_video = "video_ext" in download_settings
            has_audio = "audio_ext" in download_settings

            if has_video:
                video_locations[folder_name] = download_settings
            if has_audio:
                audio_locations[folder_name] = download_settings

        return audio_locations, video_locations
