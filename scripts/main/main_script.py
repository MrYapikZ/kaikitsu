import sys
import json
import time
import requests
from scripts.main.request.api import RequestAPI

class MainHandler(RequestAPI):
    def __init__(self):
        super().__init__()
