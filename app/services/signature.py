import json
from pathlib import Path
from typing import Any, Dict

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


def _canonical_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _compute_hash(payload: Dict[str, Any]) -> SHA256.SHA256Hash:
    data = _canonical_json(payload).encode("utf-8")
    return SHA256.new(data)


def sign_hardware_fingerprint(private_key_pem: bytes, payload: Dict[str, Any]) -> bytes:
    key = RSA.import_key(private_key_pem)
    digest = _compute_hash(payload)
    return pkcs1_15.new(key).sign(digest)


def verify_hardware_fingerprint(public_key_pem: bytes, payload: Dict[str, Any], signature: bytes) -> bool:
    key = RSA.import_key(public_key_pem)
    digest = _compute_hash(payload)
    try:
        pkcs1_15.new(key).verify(digest, signature)
        return True
    except (ValueError, TypeError):
        return False


def load_key(path: Path) -> bytes:
    return Path(path).read_bytes()
