import sqlite3
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os
from app.services.crypto import decrypt_file, encrypt_file, derive_key, decrypt_aes_cfb, encrypt_aes_cfb
from app.core.config import settings

Base = declarative_base()

_engine = None
SessionLocal = None
_mem_conn = None


def init_encrypted_db(password: str):
    global _engine, SessionLocal, _mem_conn

    salt = b"my_salt"
    key = derive_key(password, salt)

    if os.path.exists("users.db.enc"):
        with open("users.db.enc", "rb") as f:
            enc_data = f.read()
        try:
            db_bytes = decrypt_aes_cfb(key, enc_data)
        except Exception:
            raise Exception("Неверная парольная фраза!")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            tmp_name = tmp.name
            tmp.write(db_bytes)

        try:
            disk_conn = sqlite3.connect(tmp_name)
            _mem_conn = sqlite3.connect(":memory:")
            disk_conn.backup(_mem_conn)
        finally:
            disk_conn.close()
            os.remove(tmp_name)

    else:
        _mem_conn = sqlite3.connect(":memory:")

    _engine = create_engine("sqlite:///:memory:", creator=lambda: _mem_conn)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    from app.models.user import User
    Base.metadata.create_all(bind=_engine)


def save_encrypted_db(password: str):
    global _mem_conn
    salt = b"my_salt"
    key = derive_key(password, salt)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp_name = tmp.name

    try:
        disk_conn = sqlite3.connect(tmp_name)
        _mem_conn.backup(disk_conn)
        disk_conn.close()

        with open(tmp_name, "rb") as f:
            db_bytes = f.read()

        enc_data = encrypt_aes_cfb(key, db_bytes)

        with open("users.db.enc", "wb") as f:
            f.write(enc_data)

    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
