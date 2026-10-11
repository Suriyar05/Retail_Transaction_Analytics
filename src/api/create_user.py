
from getpass import getpass

from pwdlib import PasswordHash
from sqlalchemy import text

from src.api.database import SessionLocal

password_hash = PasswordHash.recommended()


def main():
    username = input("Username: ").strip()
    if not username:
        raise SystemExit("Username cannot be empty.")

    role = input("Role (analyst/admin): ").strip().lower()
    if role not in {"analyst", "admin"}:
        raise SystemExit("Role must be analyst or admin.")

    password = getpass("Password (minimum 12 characters): ")
    confirm = getpass("Confirm password: ")

    if len(password) < 12:
        raise SystemExit("Password must be at least 12 characters.")
    if password != confirm:
        raise SystemExit("Passwords do not match.")

    db = SessionLocal()
    try:
        existing = db.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": username},
        ).first()

        if existing:
            raise SystemExit("That username already exists.")

        db.execute(
            text("""
                INSERT INTO users (username, password_hash, role)
                VALUES (:username, :password_hash, :role)
            """),
            {
                "username": username,
                "password_hash": password_hash.hash(password),
                "role": role,
            },
        )
        db.commit()
        print(f"Created {role} account: {username}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
