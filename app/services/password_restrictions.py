import re


def check_password(password: str) -> str | None:
    checks = {
        "latin letters": r"[A-Za-z]",
        "cyrillic letters": r"[А-Яа-яЁё]",
        "arithmetic operators (+-*/)": r"[+\-*/]"
    }

    for name, pattern in checks.items():
        if not re.search(pattern, password):
            return f"Password must contain {name}"

    return None
