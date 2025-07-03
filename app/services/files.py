import logging
import os.path

from multipart import file_path

from app.core.app_states import AppState
from app.core.logger import get_logger
from app.core.gazu_client import gazu_client
from app.config import Settings

logger = get_logger(__name__)

class FileService:
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_preview_file_thumbnail(file_id: str) -> dict:
        """
        Download a file using Gazu client and save it to the specified path.
        """
        os.makedirs(os.path.join(Settings.FILES_DIR, "preview"), exist_ok=True)
        file_path = os.path.join(Settings.FILES_DIR, "preview", f"{file_id}.png")

        try:
            response = gazu_client.files.download_preview_file_thumbnail(file_id, file_path=file_path)
            if response:
                logger.info(f"File downloaded successfully: {file_path}")
                return {"success": True, "message": "Preview file thumbnail downloaded successfully", "file_path": file_path}
            else:
                logger.error("File download failed")
                return {"success": False, "message": "Preview file thumbnail download failed"}
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return {"success": False, "message": f"Error downloading preview file thumbnail: {str(e)}"}