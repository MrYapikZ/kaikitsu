import requests
from app.core.app_states import AppState

states = AppState()

class AuthServices:
    def __init__(self):
        super().__init__()

    @staticmethod
    def authenticate_user(email, password):
        """Make API request to authenticate user"""
        api_url = f"{states.kiyokai_url}/api/v1/auth/login"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        payload = {"username": email, "password": password, "zou_url": states.zou_url}

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            print(f"JSON: {response.json()}")
            return response.json(), response.cookies
        except requests.RequestException as e:
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def api_req_logout():
        """Make API request to authenticate user"""
        api_url = f"{states.kiyokai_url}/api/v1/auth/logout"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.post(api_url, headers=headers)
            print(f"JSON: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "message": f"Network error: {e}"}

