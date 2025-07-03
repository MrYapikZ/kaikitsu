import requests

from app.core.logger import get_logger

logger = get_logger(__name__)

class ZouService:
    """Service for interacting with Zou API"""

    @staticmethod
    def get_zou_url(api_url, params=None):
        """Fetch data from Zou API"""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        kiyokai_url = f"{api_url}/api/v1/zou/api"

        try:
            response = requests.get(kiyokai_url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            if response.status_code != 200:
                logger.error(f"Failed to fetch data from Zou API: {response.status_code} - {response.text}")
                return {"success": False, "message": "Failed to fetch data from Zou API."}
            logger.info(f"Zou API response: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}