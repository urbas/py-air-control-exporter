import pytest

from py_air_control_exporter.fetchers import coap_philips


def test_encryption_decryption_cycle():
    encryption_context = coap_philips.EncryptionContext()
    encryption_context.set_session_key("abcd")
    payload = "hello world"
    encrypted_payload = encryption_context.encrypt(payload)
    assert encrypted_payload != payload
    assert encryption_context.decrypt(encrypted_payload) == payload


def test_encryption_without_session_key():
    with pytest.raises(coap_philips.SessionKeyInitError):
        coap_philips.EncryptionContext().encrypt("Hello")


def test_digest_mismatch():
    encryption_context = coap_philips.EncryptionContext()
    encryption_context.set_session_key("abcd")
    encrypted_payload = encryption_context.encrypt("hello world")
    encrypted_payload = encrypted_payload[0:-64] + ("0" * 64)
    with pytest.raises(coap_philips.DigestMismatchError):
        encryption_context.decrypt(encrypted_payload)
