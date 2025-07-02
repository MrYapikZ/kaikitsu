import requests
from app.core.app_states import AppState

state = AppState()

class ProjectService:
    @staticmethod
    def get_project_list(cookies):
        """Make API request to authenticate user"""
        api_url = f"{state.kiyokai_url}/api/v1/projects"

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
        api_url = f"{state.kiyokai_url}/api/v1/projects/{project_id}/metadata"

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
        api_url = f"{state.kiyokai_url}/api/v1/projects/{project_id}/metadata/{metadata_id}"

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
        api_url = f"{state.kiyokai_url}/api/v1/projects/{project_id}/metadata/{metadata_id}/version"

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
        api_url = f"{state.kiyokai_url}/api/v1/projects/{project_id}/metadata/{metadata_id}/version/{version_id}"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.get(api_url, headers=headers, cookies=cookies)
            print(f"JSON: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "message": f"Network error: {e}"}