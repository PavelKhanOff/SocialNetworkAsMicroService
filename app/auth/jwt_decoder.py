import jwt
from typing import Optional
from app.config import SECRET


async def decode(token: Optional[str]):
    if not token:
        return None
    token = token.split()
    if len(token) != 2:
        return None
    if token[0].lower() != "bearer":
        return None
    token = token[1]
    if token is None:
        return None
    try:
        data = jwt.decode(
            token,
            SECRET,
            audience=["fastapi-users:auth"],
            algorithms=["HS256"],
        )
        user_id = data.get("user_id")
        if user_id is None:
            return None
    except jwt.PyJWTError:
        return None
    return user_id
