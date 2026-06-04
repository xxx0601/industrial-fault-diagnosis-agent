"""Extract fault codes from text tokens and log lines."""

import re

_FAULT_CODE_PATTERN = re.compile(r"^E\d{3,4}$", re.IGNORECASE)
_INLINE_FAULT_PATTERN = re.compile(r"\b(E\d{3,4})\b", re.IGNORECASE)


def normalize_fault_code(token: str | None) -> str | None:
    if not token:
        return None
    code = token.strip().upper()
    if _FAULT_CODE_PATTERN.match(code):
        return code
    return None


def extract_fault_code_from_token(token: str) -> str | None:
    """Return E-code if token is or contains a fault code."""
    direct = normalize_fault_code(token)
    if direct:
        return direct
    match = _INLINE_FAULT_PATTERN.search(token)
    if match:
        return match.group(1).upper()
    return None


def is_normal_status(token: str | None) -> bool:
    if not token:
        return False
    return token.strip().upper() in {"NORMAL", "OK", "HEALTHY", "RUNNING"}
