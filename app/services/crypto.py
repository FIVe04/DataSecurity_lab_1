import hashlib
import os

from app.utils.crypto_utils import generate_permutation_key, apply_permutation, gamma_transform, \
    apply_inverse_permutation

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def get_password_hash(username: str, password: str) -> str:
    key = generate_permutation_key(username, len(username))
    permuted = apply_permutation(password, key)

    encrypted_bytes = gamma_transform(permuted.encode("utf-8"))

    return encrypted_bytes.hex()


def decrypt_password(username: str, hashed_password: str) -> str:
    encrypted_bytes = bytes.fromhex(hashed_password)
    decrypted_bytes = gamma_transform(encrypted_bytes)
    key = generate_permutation_key(username, len(username))
    return apply_inverse_permutation(decrypted_bytes.decode("utf-8"), key)


def verify_password(username: str, plain_password: str, hashed_password: str) -> bool:
    decrypted = decrypt_password(username, hashed_password)
    return decrypted == plain_password


def derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.md5(password.encode() + salt).digest()


def encrypt_aes_cfb(key: bytes, data: bytes) -> bytes:
    iv = os.urandom(16)  # случайный IV
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(data) + encryptor.finalize()
    return iv + ct


def decrypt_aes_cfb(key: bytes, enc_data: bytes) -> bytes:
    iv, ct = enc_data[:16], enc_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ct) + decryptor.finalize()


def encrypt_file(key: bytes, infile: str, outfile: str):
    with open(infile, "rb") as f:
        data = f.read()
    enc_data = encrypt_aes_cfb(key, data)
    with open(outfile, "wb") as f:
        f.write(enc_data)


def decrypt_file(key: bytes, infile: str, outfile: str):
    with open(infile, "rb") as f:
        enc_data = f.read()
    data = decrypt_aes_cfb(key, enc_data)
    with open(outfile, "wb") as f:
        f.write(data)





