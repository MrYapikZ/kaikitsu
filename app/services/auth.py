import logging
from app.core.app_states import AppState
from app.core.gazu_client import gazu_client
from app.config import Settings

logger = logging.getLogger(__name__)

states = AppState()

class AuthServices:
    def __init__(self):
        super().__init__()

    @staticmethod
    def authenticate_user(email: str, password: str) -> dict:
        """
        Authenticate user using Gazu and return structured response.
        """
        try:
            user = gazu_client.log_in(email, password)

            if user and "login" in user:
                Settings.SESSION_FILE = user
                gazu_client.files.download_person_avatar(user["user"]["id"], file_path=Settings.AVATAR_FILE)

                logger.info(f"User authenticated: {user.get('first_name', '')} {user.get('last_name', '')}")
                return {
                    "success": True,
                    "message": "Authentication successful",
                    "user": user
                }
            else:
                logger.error("Authentication failed: User data not found")
                return {
                    "success": False,
                    "message": "Authentication failed: User data not found"
                }

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {
                "success": False,
                "message": f"Authentication failed: {str(e)}"
            }

    @staticmethod
    def api_req_logout() -> dict:
        """
        Log out current user using Gazu client.
        """
        try:
            gazu_client.log_out()
            logger.info("User logged out.")
            return {
                "success": True,
                "message": "Successfully logged out"
            }

        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return {
                "success": False,
                "message": f"Logout failed: {str(e)}"
            }