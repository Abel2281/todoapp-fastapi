import jwt
from datetime import datetime, timedelta, timezone
import schemas
from jwt.exceptions import InvalidTokenError
import os
from dotenv import load_dotenv 

load_dotenv()

KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    if not KEY:
        raise ValueError("SECRET_KEY environment variable is not set")
    encoded_jwt = jwt.encode(to_encode, KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        if not KEY:
            raise ValueError("SECRET_KEY environment variable is not set")
        payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        return schemas.TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception