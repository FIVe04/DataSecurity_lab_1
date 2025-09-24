from typing import List


def generate_permutation_key(username: str, block_size: int) -> List[int]:
    t = username
    t_sorted = sorted(t)

    used = [False] * len(t_sorted)
    key = []

    for ch in t:
        for i, sorted_ch in enumerate(t_sorted):
            if sorted_ch == ch and not used[i]:
                key.append(i)
                used[i] = True
                break

    if len(key) > block_size:
        key = key[:block_size]
    elif len(key) < block_size:
        key = (key * ((block_size // len(key)) + 1))[:block_size]

    return key


def apply_permutation(text: str, key: List[int]) -> str:
    n = len(key)
    blocks = [text[i:i + n] for i in range(0, len(text), n)]

    result = []
    for block in blocks:
        block = block.ljust(n)
        result.append("".join(block[k] for k in key))
    return "".join(result)


def apply_inverse_permutation(text: str, key: List[int]) -> str:
    n = len(key)
    inv_key = [0] * n
    for i, k in enumerate(key):
        inv_key[k] = i

    blocks = [text[i:i + n] for i in range(0, len(text), n)]

    result = []
    for block in blocks:
        block = block.ljust(n)
        result_block = [""] * n
        for i, k in enumerate(inv_key):
            result_block[i] = block[k]
        result.append("".join(result_block))
    return "".join(result).rstrip()


def gamma_sequence(length: int, A: int = 5, C: int = 3, G0: int = 1) -> List[int]:
    gamma = [G0]
    for _ in range(length - 1):
        gamma.append((A * gamma[-1] + C) % 256)
    return gamma


def gamma_transform(data: bytes) -> bytes:
    gamma = gamma_sequence(len(data))
    return bytes([b ^ gamma[i] for i, b in enumerate(data)])

