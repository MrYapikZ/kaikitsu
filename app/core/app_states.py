from app.core.gazu_client import gazu_client
from app.services.zou import ZouService

class AppState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)

            cls.zou_url = None
            cls.kiyokai_url = None

            cls.access_token = None
            cls.user_data = None

            cls.task_data = None

            cls._instance.cookies = None
            cls._instance.username = None
            cls._instance.avatar_url = None
        return cls._instance

    def set_kiyokai_url(self, kiyokai_url):
        self.kiyokai_url = kiyokai_url
        response = ZouService.get_zou_url(self.kiyokai_url)
        if response.get('success'):
            self.zou_url = response.get("url")
            gazu_client.set_host(self.zou_url)

    def set_user_data(self, user_data):
        self.user_data = user_data

    def set_access_token(self, access_token):
        self.access_token = access_token

    def set_task_data(self, task_data):
        self.task_data = task_data

    def is_logged_in(self):
        return self.cookies is not None
