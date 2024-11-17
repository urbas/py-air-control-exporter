import hashlib
import os

from Cryptodome.Cipher import AES, _mode_cbc
from Cryptodome.Util.Padding import pad, unpad

from py_air_control_exporter.fetchers.api import FetcherCreatorArgs
from py_air_control_exporter.metrics import Fetcher


def create_fetcher(config: FetcherCreatorArgs) -> Fetcher:
    return lambda _target_host=config.target_host: None


class SessionKeyInitError(Exception):
    pass


class DigestMismatchError(Exception):
    pass


class EncryptionContext:
    def __init__(self):
        self._session_key: str | None = None
        self._key_salt: str = os.urandom(4).hex().upper()

    def set_session_key(self, session_key) -> None:
        self._session_key = session_key

    def _increment_session_key(self) -> str:
        if self._session_key is None:
            raise SessionKeyInitError
        session_key_next = (
            (int(self._session_key, 16) + 1).to_bytes(4, byteorder="big").hex().upper()
        )
        self._session_key = session_key_next
        return session_key_next

    def _create_cipher(self, key: str) -> _mode_cbc.CbcMode:
        secret_key, iv = _create_key_and_iv(self._key_salt, key)
        return AES.new(key=secret_key, mode=AES.MODE_CBC, iv=iv)

    def encrypt(self, payload: str) -> str:
        key = self._increment_session_key()
        plaintext_padded = pad(payload.encode(), 16, style="pkcs7")
        cipher = self._create_cipher(key)
        ciphertext = cipher.encrypt(plaintext_padded).hex().upper()
        return key + ciphertext + _calculate_digest(key, ciphertext)

    def decrypt(self, payload_encrypted: str) -> str:
        key = payload_encrypted[0:8]
        ciphertext = payload_encrypted[8:-64]
        digest = payload_encrypted[-64:]
        if digest != _calculate_digest(key, ciphertext):
            raise DigestMismatchError
        cipher = self._create_cipher(key)
        plaintext_padded = cipher.decrypt(bytes.fromhex(ciphertext))
        plaintext_unpadded = unpad(plaintext_padded, 16, style="pkcs7")
        return plaintext_unpadded.decode()


def _create_key_and_iv(salt: str, key: str) -> tuple[bytes, bytes]:
    key_and_iv_digest = hashlib.md5(salt.encode())  # noqa: S324
    key_and_iv_digest.update(key.encode())
    key_and_iv = key_and_iv_digest.hexdigest().upper()
    half_keylen = len(key_and_iv) // 2
    secret_key = key_and_iv[0:half_keylen]
    iv = key_and_iv[half_keylen:]
    return (secret_key.encode(), iv.encode())


def _calculate_digest(key: str, ciphertext: str) -> str:
    digest = hashlib.sha256(key.encode())
    digest.update(ciphertext.encode())
    return digest.hexdigest().upper()
