from app.core.gazu_client import gazu_client
from app.core.logger import get_logger

logger = get_logger(__name__)

class AssetService:
    """Service for interacting with Asset API"""

    @staticmethod
    def get_asset_types_by_project(project_id: str):
        """Fetch assets by project ID"""

        try:
            response = gazu_client.asset.all_asset_types_for_project(project_id)
            logger.info(f"Project asset list: {response}")
            return response
        except Exception as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}

    @staticmethod
    def get_asset_metadata(asset_id: str):
        """Fetch asset metadata by asset ID"""

        try:
            response = gazu_client.asset.get_asset(asset_id)
            logger.info(f"Asset metadata: {response}")
            return response
        except Exception as e:
            logger.error(f"Network error: {e}")
            return {"success": False, "message": f"Network error: {e}"}