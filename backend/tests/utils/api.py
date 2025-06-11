import requests

class APIClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or "http://127.0.0.1:8000"
        self.session = requests.Session()
        self.token = None
        self.data = None

    def set_auth(self, token):
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def post(self, path, data=None):
        resp = self.session.post(f"{self.base_url}{path}", json=data)
        self.data = self._parse(resp)
        return resp

    def get(self, path, params=None):
        resp = self.session.get(f"{self.base_url}{path}", params=params)
        self.data = self._parse(resp)
        return resp

    def _parse(self, resp):
        try:
            return resp.json()
        except Exception:
            return None 