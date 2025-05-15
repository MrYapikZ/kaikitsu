import requests

ROOT_URL="https://expiproject.com"

class RequestAPI:
    def __init__(self):
        super().__init__()

    @staticmethod
    def authenticate_user(email, password):
        """Make API request to authenticate user"""
        api_url = f"{ROOT_URL}/api/v1/launcher/auth/login"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        payload = {"username": email, "password": password}

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            print(f"JSON: {response.json()}")
            return response.json(), response.cookies
        except requests.RequestException as e:
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def api_req_logout():
        """Make API request to authenticate user"""
        api_url = f"{ROOT_URL}/api/v1/launcher/auth/logout"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.post(api_url, headers=headers)
            print(f"JSON: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def get_project_list(cookies):
        """Make API request to authenticate user"""
        api_url = f"{ROOT_URL}/api/v1/launcher/projects"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.get(api_url, headers=headers, cookies=cookies)
            print(f"JSON: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def get_metadata_list(cookies, project_id):
        """Make API request to authenticate user"""
        api_url = f"{ROOT_URL}/api/v1/launcher/projects/{project_id}/metadata"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.get(api_url, headers=headers, cookies=cookies)
            print(f"JSON: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def get_metadata(cookies, project_id, metadata_id):
        """Make API request to authenticate user"""
        api_url = f"{ROOT_URL}/api/v1/launcher/projects/{project_id}/metadata/{metadata_id}"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.get(api_url, headers=headers, cookies=cookies)
            print(f"JSON: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def get_version_list(cookies, project_id, metadata_id):
        """Make API request to authenticate user"""
        api_url = f"{ROOT_URL}/api/v1/launcher/projects/{project_id}/metadata/{metadata_id}/version"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.get(api_url, headers=headers, cookies=cookies)
            print(f"JSON: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def get_version(cookies, project_id, metadata_id, version_id):
        """Make API request to authenticate user"""
        api_url = f"{ROOT_URL}/api/v1/launcher/projects/{project_id}/metadata/{metadata_id}/version/{version_id}"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.get(api_url, headers=headers, cookies=cookies)
            print(f"JSON: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "message": f"Network error: {e}"}