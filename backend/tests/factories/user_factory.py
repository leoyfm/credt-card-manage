import uuid

def build_user(**kwargs):
    username = kwargs.get("username") or f"user_{uuid.uuid4().hex[:8]}"
    email = kwargs.get("email") or f"{username}@example.com"
    password = kwargs.get("password") or "TestPass123456"
    return {"username": username, "email": email, "password": password} 