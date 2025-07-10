import os

from itsdangerous import BadSignature, SignatureExpired, TimestampSigner

signer = TimestampSigner(os.environ.get("SECRET_KEY", "DEFAULT_SECRET_KEY"))


def generate_signed_url(file_path: str, expires_in: int = 300) -> str:
    token = signer.sign(file_path).decode()
    return f"/api/reports/download/{token}?expires_in={expires_in}"


def verify_signed_url(signed_token: str, max_age: int = 300) -> str | None:
    try:
        original = signer.unsign(signed_token, max_age=max_age)
        return original.decode()
    except (BadSignature, SignatureExpired):
        return None
