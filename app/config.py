import os
import platform

from app.core.app_states import AppState


def get_config_dir(app_name="myapp") -> str:
    system = platform.system()

    if system == "Windows":
        return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming")), app_name)
    elif system == "Darwin":  # macOS
        return os.path.join(os.path.expanduser("~/Library/Application Support"), app_name)
    else:  # Linux and others
        return os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), app_name)

class Settings:
    APP_NAME = "Kaikatsu"
    CONFIG_DIR = get_config_dir(APP_NAME)
    SESSION_FILE = os.path.join(CONFIG_DIR, "gazu_session.json")
    AVATAR_FILE = os.path.join(CONFIG_DIR, "files", "avatar.png")

    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(AVATAR_FILE), exist_ok=True)