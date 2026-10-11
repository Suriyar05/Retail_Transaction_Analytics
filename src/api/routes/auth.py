
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from pwdlib import PasswordHash
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.auth import create_access_token, get_current_user
from src.api.database import get_db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
password_hash = PasswordHash.recommended()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.execute(
        text("""
            SELECT id, username, password_hash, role
            FROM users
            WHERE username = :username
        """),
        {"username": credentials.username},
    ).mappings().first()

    # Use the same response for an unknown username and wrong password.
    if not user or not password_hash.verify(
        credentials.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token(user["username"])

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user["username"],
        "role": user["role"],
    }


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
