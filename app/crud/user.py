from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.database import get_db


def get_user_by_username(db: Session, username: str) -> User:
    print('get')
    return db.query(User).filter(User.username == username).first()


def add_admin(db: Session):
    user = User(username="admin", hashed_password="", role='admin', is_locked=False, password_restrictions_enabled=True)
    db.add(user)
    db.commit()


def add_user(db: Session, user: User) -> User:
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise ValueError("Username already exists")


def register_user(db: Session, user: User) -> User:
    existing_user = db.query(User).filter(User.username == user.username).first()
    if not existing_user:
        raise ValueError("No such user")
    else:
        if existing_user.hashed_password == "":
            existing_user.hashed_password = user.hashed_password
            db.commit()
            db.refresh(existing_user)
            return existing_user
        else:
            raise ValueError("Already have an account")


def get_user_by_id(db: Session, user_id: int) -> User:
    print(db.query(User).filter(User.id == user_id).first())
    return db.query(User).filter(User.id == user_id).first()


def update_user_password(db: Session, user_id: int, new_hash_password: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise ValueError(f"Пользователь с ID {user_id} не найден")

    user.hashed_password = new_hash_password

    db.commit()
    db.refresh(user)

    return user


def get_all_users(db: Session) -> List[User]:
    return db.query(User).all()


def block_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise ValueError(f"User not found")

    user.is_locked = not user.is_locked

    db.commit()
    db.refresh(user)

    return user


def restrict_password_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise ValueError(f"User not found")

    user.password_restrictions_enabled = not user.password_restrictions_enabled

    db.commit()
    db.refresh(user)

    return user
