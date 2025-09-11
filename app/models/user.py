from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from app.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, nullable=True)
    is_locked = Column(Boolean, default=False)
    password_restrictions_enabled = Column(Boolean, default=True)
