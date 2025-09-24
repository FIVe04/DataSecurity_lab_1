from app.utils.crypto_utils import generate_permutation_key, apply_permutation, gamma_transform, \
    apply_inverse_permutation


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



