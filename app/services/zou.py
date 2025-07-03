import requests

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
                return {"success": False, "message": "Failed to fetch data from Zou API."}
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "message": f"Network error: {e}"}