import asyncio
import hashlib
import json
import logging
import multiprocessing
import os

from aiocoap import (
    GET,
    NON,
    POST,
    Context,
    Message,
)
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad

from py_air_control_exporter import fetchers_api
from py_air_control_exporter.fetchers import http_philips

LOG = logging.getLogger(__name__)


def create_fetcher(config: fetchers_api.FetcherCreatorArgs) -> fetchers_api.Fetcher:
    return lambda target_host=config.target_host: get_status_subprocess(target_host)


async def get_status(host, timeout_seconds: float | None) -> dict | None:
    try:
        async with asyncio.timeout(timeout_seconds), Client(host=host) as client:
            return await client.get_status()
    except TimeoutError:
        LOG.error("Timed out while fetching the status from '%s'.", host)
        LOG.debug("Timeout error stack trace:", exc_info=True)
        return None


def get_status_sync(host: str, timeout_seconds: float | None) -> dict | None:
    return asyncio.run(get_status(host, timeout_seconds))


def get_status_subprocess(host: str) -> fetchers_api.TargetReading | None:
    with multiprocessing.Pool(1) as process_pool:
        timeout_seconds = 20
        status_data = process_pool.apply(get_status_sync, args=(host, timeout_seconds))
        if status_data is None:
            return None
        return fetchers_api.TargetReading(
            air_quality=http_philips.create_air_quality(status_data),
            control_info=http_philips.create_control_info(status_data),
            filters=http_philips.create_filter_info(status_data),
        )


class ClientNotInitializedError(Exception):
    pass


class Client:
    STATUS_PATH = "/sys/dev/status"
    SYNC_PATH = "/sys/dev/sync"

    def __init__(self, host, port=5683):
        self.host = host
        self.port = port
        self._client_context = None

    async def __aenter__(self):
        self._client_context = await Context.create_client_context()
        await self._sync()
        return self

    async def __aexit__(self, *_exc):
        if self._client_context:
            await self._client_context.shutdown()
        return False

    async def _sync(self):
        if self._client_context is None:
            raise ClientNotInitializedError
        uri = f"coap://{self.host}:{self.port}{self.SYNC_PATH}"
        LOG.debug("Syncing with '%s'...", uri)
        sync_request = os.urandom(4).hex().upper().encode()
        request = Message(code=POST, mtype=NON, uri=uri, payload=sync_request)
        response = await self._client_context.request(request).response
        client_key = response.payload.decode()
        LOG.debug("Successfully synced with '%s'. Client key: '%s'", uri, client_key)

    async def get_status(self):
        if self._client_context is None:
            raise ClientNotInitializedError
        uri = f"coap://{self.host}:{self.port}{self.STATUS_PATH}"
        LOG.debug("Fetching status from '%s'...", uri)
        request = Message(code=GET, mtype=NON, uri=uri)
        request.opt.observe = 0
        response = await self._client_context.request(request).response
        payload = decrypt(response.payload.decode())
        LOG.debug("Got status from '%s': %s", uri, payload)
        return json.loads(payload)["state"]["reported"]


class SessionKeyInitError(Exception):
    pass


class DigestMismatchError(Exception):
    pass


def decrypt(payload_encrypted: str) -> str:
    key = payload_encrypted[0:8]
    ciphertext = payload_encrypted[8:-64]
    digest = payload_encrypted[-64:]
    if digest != _calculate_digest(key, ciphertext):
        raise DigestMismatchError
    cipher = _create_cipher(key)
    plaintext_padded = cipher.decrypt(bytes.fromhex(ciphertext))
    return unpad(plaintext_padded, 16, style="pkcs7").decode()


def _create_cipher(key: str):
    key_and_iv = hashlib.md5(("JiangPan" + key).encode()).hexdigest().upper()  # noqa: S324
    half_keylen = len(key_and_iv) // 2
    secret_key = key_and_iv[0:half_keylen]
    iv = key_and_iv[half_keylen:]
    return AES.new(key=secret_key.encode(), mode=AES.MODE_CBC, iv=iv.encode())


def _calculate_digest(key: str, ciphertext: str) -> str:
    digest = hashlib.sha256(key.encode())
    digest.update(ciphertext.encode())
    return digest.hexdigest().upper()
