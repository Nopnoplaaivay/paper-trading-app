import os

class WebConfigs:
    BASE_API_URL = f"http://{os.getenv('BACKEND_HOST')}:4000/api/v1"