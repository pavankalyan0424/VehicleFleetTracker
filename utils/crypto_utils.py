from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64
from dotenv import load_dotenv

load_dotenv()
key = bytes.fromhex(os.getenv("SECRET_KEY"))

def encrypt(value: str) -> str:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit recommended nonce
    ciphertext = aesgcm.encrypt(nonce, value.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()

def decrypt(value: str) -> str:
    aesgcm = AESGCM(key)
    decoded = base64.b64decode(value.encode())
    nonce = decoded[:12]
    ciphertext = decoded[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()

