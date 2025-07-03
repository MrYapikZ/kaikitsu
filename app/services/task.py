import logging
from app.core.app_states import AppState
from app.core.gazu_client import gazu_client
from app.config import Settings

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_task_list(user_id: str = None):
        """Make API request to get task list for a project"""

        try:
            response = gazu_client.user.all_tasks_to_do()
            logger.info(f"Task List: {response}")
            return response
        except Exception as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}