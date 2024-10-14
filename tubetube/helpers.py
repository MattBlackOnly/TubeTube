import re


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

def trim_description(info_dict):
    description = info_dict.get("description", "")
    max_length = 250
    if len(description) > max_length:
        info_dict["description"] = description[:max_length] + "..."
