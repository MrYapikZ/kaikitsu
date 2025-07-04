from app.core.gazu_client import gazu_client
from app.core.logger import get_logger

logger = get_logger(__name__)

class ProjectService:
    """Service for interacting with Project API"""

    @staticmethod
    def get_user_project():
        """Fetch data from Project API"""

        try:
            response = gazu_client.user.all_open_projects()
            logger.info(f"User project list: {response}")
            return response
        except Exception as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def get_project_metadata(project_id: str):
        """Fetch project metadata by project ID"""

        try:
            response = gazu_client.project.get_project(project_id)
            logger.info(f"Project metadata: {response}")
            return response
        except Exception as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}