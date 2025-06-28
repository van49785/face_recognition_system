# Hàm JWT, mã hóa mật khẩu, xác thực token
import os
import bcrypt
from datetime import datetime, timezone, timedelta
import jwt

JWT_SECRET = os.getenv("SECRET_KEY", "jwt-secret")
JWT_ALG = "HS256"
JWT_EXPIRES_SECONDS = int(os.getenv("JWT_EXPIRES", 7200))


# ---------------  Password helpers  ------------------

def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode(), salt).decode()

def check_password_hash(hashed: str, plain: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# ---------------  JWT helpers  ------------------

def generate_jwt_token(admin_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(admin_id),
        "iat": now,
        "exp": now + timedelta(seconds=JWT_EXPIRES_SECONDS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_jwt_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


