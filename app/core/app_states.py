from app.core.gazu_client import gazu_client

class AppState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)

            cls.zou_url = None
            cls.kiyokai_url = None

            cls.access_token = None
            cls.user_data = None

            cls._instance.cookies = None
            cls._instance.username = None
            cls._instance.avatar_url = None
        return cls._instance

    def set_url_data(self, zou_url, kiyokai_url):
        self.zou_url = zou_url
        self.kiyokai_url = kiyokai_url
        gazu_client.set_host(self.zou_url)

    def set_user_data(self, user_data):
        self.user_data = user_data

    def set_access_token(self, access_token):
        self.access_token = access_token

    def is_logged_in(self):
        return self.cookies is not None