import logging
import httpx
from app.core.app_states import AppState
from app.core.logger import get_logger
from app.config import Settings

logger = get_logger(__name__)

class KiyokaiService:
    def __init__(self):
        super().__init__()

    @staticmethod
    def set_kiyokai_url(kiyokai_url: str) -> dict:
        """
        Set the Kiyokai URL and update the ZOU URL accordingly.
        """
        try:
            AppState().set_kiyokai_url(kiyokai_url)
            logger.info(f"Kiyokai URL set to: {kiyokai_url}")
            return {
                "success": True,
                "message": "Kiyokai URL updated successfully"
            }
        except Exception as e:
            logger.error(f"Failed to set Kiyokai URL: {e}")
            return {
                "success": False,
                "message": f"Failed to set Kiyokai URL: {str(e)}"
            }

    @staticmethod
    def get_master_shot_data_by_id(shot_id: str, task_id: str) -> dict:
        """
        Fetch master shot data by ID from Kiyokai API.
        """
        kiyokai_url = AppState().kiyokai_url
        token = AppState().access_token
        if not kiyokai_url or not token:
            logger.error("Kiyokai URL is not set.")
            return {
                "success": False,
                "message": "Kiyokai URL is not set."
            }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            response = httpx.get(f"{kiyokai_url}/api/v1/mastershots/list/{shot_id}/tasks/{task_id}", headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            logger.info(f"Master shot data retrieved successfully: {response.json()}")
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Request error while fetching master shot data: {e}")
            return {
                "success": False,
                "message": f"Request error: {str(e)}"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while fetching master shot data: {e}")
            return {
                "success": False,
                "message": f"HTTP error: {str(e)}"
            }

    @staticmethod
    def create_master_shot(data: dict) -> dict:
        """
        Create a new master shot in Kiyokai.
        """
        kiyokai_url = AppState().kiyokai_url
        token = AppState().access_token
        if not kiyokai_url or not token:
            logger.error("Kiyokai URL is not set.")
            return {
                "success": False,
                "message": "Kiyokai URL is not set."
            }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            response = httpx.post(f"{kiyokai_url}/api/v1/mastershots/create", json=data, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            logger.info(f"Master shot created successfully: {response.json()}")
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Request error while creating master shot: {e}")
            return {
                "success": False,
                "message": f"Request error: {str(e)}"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while creating master shot: {e}")
            return {
                "success": False,
                "message": f"HTTP error: {str(e)}"
            }

    @staticmethod
    def create_nas_server(data: dict) -> dict:
        """
        Create a new NAS server in Kiyokai.
        """
        kiyokai_url = AppState().kiyokai_url
        token = AppState().access_token

        if not kiyokai_url or not token:
            logger.error("Kiyokai URL is not set.")
            return {
                "success": False,
                "message": "Kiyokai URL is not set."
            }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            response = httpx.post(f"{kiyokai_url}/api/v1/nas/create", json=data, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            logger.info(f"NAS server created successfully: {response.json()}")
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Request error while creating NAS server: {e}")
            return {
                "success": False,
                "message": f"Request error: {str(e)}"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while creating NAS server: {e}")
            return {
                "success": False,
                "message": f"HTTP error: {str(e)}"
            }

    @staticmethod
    def get_nas_server_list() -> dict:
        """
        Fetch the list of NAS servers from Kiyokai.
        """
        kiyokai_url = AppState().kiyokai_url
        token = AppState().access_token

        if not kiyokai_url or not token:
            logger.error("Kiyokai URL is not set.")
            return {
                "success": False,
                "message": "Kiyokai URL is not set."
            }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            response = httpx.get(f"{kiyokai_url}/api/v1/nas/list", headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            logger.info(f"NAS server list retrieved successfully: {response.json()}")
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Request error while fetching NAS server list: {e}")
            return {
                "success": False,
                "message": f"Request error: {str(e)}"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while fetching NAS server list: {e}")
            return {
                "success": False,
                "message": f"HTTP error: {str(e)}"
            }