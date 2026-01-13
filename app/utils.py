from jose import jwt
import os
SECRET = os.getenv("JWT_SECRET", "changeme")
def create_token(user_id: str):
    return jwt.encode({"sub": user_id}, SECRET, algorithm="HS256")
def get_user_id_from_token(token: str):
    token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token
    data = jwt.decode(token, SECRET, algorithms=["HS256"])
    return data.get("sub")
def create_admin_token(admin_username: str):
    payload = {"sub": admin_username, "is_admin": True}
    return jwt.encode(payload, SECRET, algorithm="HS256")
def is_admin_token(token: str) -> bool:
    token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token
    try:
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        return bool(data.get("is_admin"))
    except Exception:
        return False
