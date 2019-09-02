import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import json
import random
import requests

DH_PUBLIC_BASE = int(
    "A4D1CBD5C3FD34126765A442EFB99905F8104DD258AC507FD6406CFF14266D31266FEA1E5C41564B777E690F5504F213160217B4B01B88"
    "6A5E91547F9E2749F4D7FBD7D3B9A92EE1909D0D2263F80A76A6A24C087A091F531DBF0A0169B6A28AD662A4D18E73AFA32D779D5918D0"
    "8BC8858F4DCEF97C2A24855E6EEB22B3B2E5",
    16,
)
DH_PUBLIC_MODULUS = int(
    "B10B8F96A080E01DDE92DE5EAE5D54EC52C99FBCFB06A3C69A6A9DCA52D23B616073E28675A23D189838EF1E2EE652C013ECB4AEA90611"
    "2324975C3CD49B83BFACCBDD7D90C4BD7098488E9C219A73724EFFD6FAE5644738FAA31A4FF55BCCC0A151AF5F0DC8B4BD45BF37DF365C"
    "1A65E68CFDA76D4DA708DF1FB2BC2E4A4371",
    16,
)


def get_status(host):
    return json.loads(
        dh_decrypt(
            requests.get("http://{}/di/v1/products/1/air".format(host)).text,
            get_key(host),
        )
    )


def get_key(host):
    url = "http://{}/di/v1/products/0/security".format(host)
    private_key = random.getrandbits(256)
    public_key = pow(DH_PUBLIC_BASE, private_key, DH_PUBLIC_MODULUS)
    data = json.dumps({"diffie": format(public_key, "x")})
    data_enc = data.encode("ascii")
    security_info = requests.put(url=url, data=data_enc).json()
    key = security_info["key"]
    philips_public_key = int(security_info["hellman"], 16)
    shared_secret_key = pow(philips_public_key, private_key, DH_PUBLIC_MODULUS)
    shared_secret_key_bytes = shared_secret_key.to_bytes(128, byteorder="big")[:16]
    session_key = aes_decrypt(bytes.fromhex(key), shared_secret_key_bytes)
    return session_key[:16]


def dh_decrypt(data, key):
    decrypted_data = aes_decrypt(base64.b64decode(data), key)
    response = unpad(decrypted_data, 16, style="pkcs7")[2:]
    return response.decode("ascii")


def aes_decrypt(data, key):
    iv = bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(data)
