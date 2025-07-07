from app.core.gazu_client import gazu_client
from app.core.logger import get_logger

logger = get_logger(__name__)

class ShotService:
    """Service for interacting with Shot API"""

    @staticmethod
    def get_shots_by_sequence(sequence_id: str):
        """Fetch data from Shot API"""

        try:
            response = gazu_client.shot.all_shots_for_sequence(sequence_id)
            logger.info(f"Project shot list: {response}")
            return response
        except Exception as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def get_sequence_by_episode(episode_id: str):
        """Fetch sequence by project ID"""

        try:
            response = gazu_client.shot.all_sequences_for_episode(episode_id)
            logger.info(f"Shot sequence: {response}")
            return response
        except Exception as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def get_episode_by_project(project_id: str):
        """Fetch episode by project ID"""

        try:
            response = gazu_client.shot.all_episodes_for_project(project_id)
            logger.info(f"Shot episode: {response}")
            return response
        except Exception as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def get_sequence_by_name(project_id: str, episode_id: str, sequence_name: str):
        """Fetch sequence by name"""

        try:
            response = gazu_client.shot.get_sequence_by_name(project=project_id, episode=episode_id, sequence_name=sequence_name)
            logger.info(f"Shot sequence by name: {response}")
            return response
        except Exception as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}