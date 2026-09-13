import hashlib
import hmac

from gateway.security.signature import calculate_meta_signature, verify_meta_signature


def test_verify_valid_signature() -> None:
    secret = "secret_key_xyz"
    payload = b'{"test": "payload"}'
    valid_signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    assert verify_meta_signature(payload, valid_signature, secret) is True


def test_verify_tampered_payload() -> None:
    secret = "secret_key_xyz"
    payload = b'{"test": "payload"}'
    valid_signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    tampered_payload = b'{"test": "tampered"}'

    assert verify_meta_signature(tampered_payload, valid_signature, secret) is False


def test_verify_invalid_secret() -> None:
    secret = "secret_key_xyz"
    payload = b'{"test": "payload"}'
    valid_signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    assert verify_meta_signature(payload, valid_signature, "wrong_secret") is False


def test_missing_or_malformed_prefix() -> None:
    secret = "secret_key_xyz"
    payload = b'{"test": "payload"}'
    raw_hex = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    # Missing sha256= prefix
    assert verify_meta_signature(payload, raw_hex, secret) is False
    assert verify_meta_signature(payload, "", secret) is False
    assert verify_meta_signature(payload, "sha1=" + raw_hex, secret) is False


def test_calculate_meta_signature() -> None:
    secret = "secret_key_xyz"
    payload = b'{"message": "hello"}'
    sig = calculate_meta_signature(payload, secret)
    assert sig.startswith("sha256=")
    assert verify_meta_signature(payload, sig, secret) is True
