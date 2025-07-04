import os
import platform


def get_config_dir(app_name="myapp") -> str:
    system = platform.system()

    if system == "Windows":
        return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming")), app_name)
    elif system == "Darwin":  # macOS
        return os.path.join(os.path.expanduser("~/Library/Application Support"), app_name)
    else:  # Linux and others
        return os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), app_name)


class Settings:
    APP_NAME = "Kaikitsu"
    BUILD_VERSION = "v0.0.1"

    CONFIG_DIR = get_config_dir(APP_NAME)
    SESSION_FILE = os.path.join(CONFIG_DIR, "user", "gazu_session.json")
    FILES_DIR = os.path.join(CONFIG_DIR, "files")
    AVATAR_FILE = os.path.join(FILES_DIR, "user", "avatar.png")

    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(FILES_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(AVATAR_FILE), exist_ok=True)
