import re
import yt_dlp


def parse_video_id(url):
    patterns = [
        r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/share/([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    return None


class TrimDescriptionPP(yt_dlp.postprocessor.PostProcessor):
    def run(self, info):
        description = info.get("description", "")

        if description:
            trimmed_description = description[:250]
            self.to_screen(f"Original description length: {len(description)}")
            self.to_screen(f"Trimmed description to 250 chars: {trimmed_description}")

            info["description"] = trimmed_description
        else:
            self.to_screen("No description found to trim.")

        return [], info
