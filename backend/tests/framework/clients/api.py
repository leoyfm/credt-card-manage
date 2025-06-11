import httpx

class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url)
        self.token = None

    def set_auth(self, token: str):
        self.token = token
        self.client.headers["Authorization"] = f"Bearer {token}"

    def post(self, path: str, data: dict = None):
        return self.client.post(path, json=data)

    def get(self, path: str, params: dict = None):
        return self.client.get(path, params=params) 