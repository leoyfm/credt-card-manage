class AssertResponse:
    def __init__(self, resp):
        self.resp = resp
        try:
            self.data = resp.json()
        except Exception:
            self.data = None

    def success(self):
        assert self.resp.status_code == 200, f"期望200，实际{self.resp.status_code}"
        assert self.data and self.data.get("success", True), f"响应体: {self.data}"
        return self

    def fail(self, status_code=None, code=None):
        if status_code:
            assert self.resp.status_code == status_code, f"期望失败码{status_code}，实际{self.resp.status_code}"
        else:
            assert self.resp.status_code >= 400, f"期望失败，实际{self.resp.status_code}"
        if code:
            assert self.data and self.data.get("code") == code, f"错误码不符: {self.data}"
        return self

    def with_data(self, **expected):
        actual = self.data.get("data", {}) if self.data else {}
        for k, v in expected.items():
            assert actual.get(k) == v, f"字段{k}期望{v}，实际{actual.get(k)}"
        return self

def assert_response(resp):
    return AssertResponse(resp) 