import logging
import os.path

from app.core.app_states import AppState
from app.core.logger import get_logger
from app.core.gazu_client import gazu_client
from app.config import Settings

logger = get_logger(__name__)

class TaskService:
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_tasks_by_user():
        """Make API request to get task list for a project"""

        try:
            response = gazu_client.user.all_tasks_to_do()
            logger.info(f"Task List: {response}")

            return response
        except Exception as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def get_table_task_list():
        """Make API request to get task list for a project"""

        try:
            response = gazu_client.user.all_tasks_to_do()

            if not response:
                logger.warning("No tasks found for the project.")
                return []

            extracted_data = []

            for task in response:
                last_comment = task.get("last_comment", {})

                # Handle case where person_id might be invalid or missing
                try:
                    user = gazu_client.person.get_person(last_comment.get("person_id"))
                    if not user:
                        user = {"full_name": None, "has_avatar": False, "id": None}
                except Exception as user_error:
                    logger.warning(f"Could not fetch user for person_id {last_comment.get('person_id')}: {user_error}")
                    user = {"full_name": None, "has_avatar": False, "id": None}

                avatar_path = None
                if user.get("has_avatar") and user.get("id"):
                    try:
                        os.makedirs(os.path.join(Settings.FILES_DIR, "avatar"), exist_ok=True)
                        avatar_path = os.path.join(Settings.FILES_DIR, "avatar", f"{user['id']}.png")
                        user["avatar_path"] = gazu_client.files.download_person_avatar(user["id"], file_path=avatar_path)
                    except Exception as avatar_error:
                        logger.warning(f"Could not download avatar for user {user.get('id')}: {avatar_error}")
                        avatar_path = None

                extracted_data.append({
                    "id": task.get("id"),
                    "project_name": task.get("project_name"),
                    "task_type_name": task.get("task_type_name"),
                    "task_status_name": task.get("task_status_name"),
                    "episode_name": task.get("episode_name"),
                    "sequence_name": task.get("sequence_name"),
                    "entity_name": task.get("entity_name"),
                    "entity_type_name": task.get("entity_type_name"),
                    "due_date": task.get("due_date"),
                    "priority": task.get("priority"),
                    "last_comment_person_full_name": user.get("full_name"),
                    "last_comment_text": last_comment.get("text"),
                    "last_comment_person_avatar_path": avatar_path,
                    "entity_preview_file_id": task.get("entity_preview_file_id"),
                })

            logger.info(f"Table Task List: {extracted_data}")

            return extracted_data
        except Exception as e:
            logger.error(f"Network error: {e}")
            return []  # Return empty list instead of error dictionary

    @staticmethod
    def get_task_comments(task_id: str):
        """Make API request to get comments for a task"""

        try:
            response = gazu_client.task.get_last_comment_for_task(task_id)
            logger.info(f"Task Comments: {response}")
            return response
        except Exception as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def get_task_types_by_project(project_id: str):
        """Make API request to get tasks for a project"""

        try:
            response = gazu_client.task.all_task_types_for_project(project_id)
            logger.info(f"Tasks for Project {project_id}: {response}")
            return response
        except Exception as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}