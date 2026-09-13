import hashlib
import hmac


def calculate_meta_signature(payload: bytes, secret: str) -> str:
    """Calculate the expected X-Hub-Signature-256 for a payload using the secret."""
    mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


def verify_meta_signature(payload: bytes, signature_header: str | None, secret: str) -> bool:
    """
    Verify incoming Meta WhatsApp webhook HMAC-SHA256 signature using constant-time comparison.

    Protects against timing attacks.
    """
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    received_hash = signature_header.removeprefix("sha256=").strip()
    if not received_hash:
        return False

    mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256)
    expected_hash = mac.hexdigest()

    return hmac.compare_digest(received_hash, expected_hash)
