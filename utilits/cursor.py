import base64


def encode_cursor(value: int) -> str:
    return base64.b64encode(str(value).encode()).decode()


def decode_cursor(cursor: str) -> int:
    return int(base64.b64decode(cursor).decode())