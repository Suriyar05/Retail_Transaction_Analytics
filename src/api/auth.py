
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.database import get_db

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing. Set it in your project-root .env file."
    )

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

bearer_scheme = HTTPBearer()

def create_access_token(username: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_MINUTES
    )

    payload = {
        "sub": username,
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token ,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        username = payload.get("sub")
        if not username:
            raise unauthorized
    except jwt.InvalidTokenError:
        raise unauthorized

    user = db.execute(
        text("""
            SELECT id, username, role
            FROM users
            WHERE username = :username
        """),
        {"username": username},
    ).mappings().first()

    if not user:
        raise unauthorized

    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
    }


def require_admin(
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )

    return current_user
