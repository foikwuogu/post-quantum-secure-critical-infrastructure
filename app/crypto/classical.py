import base64
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def b64(b: bytes) -> str:
    return base64.b64encode(b).decode()

def ub64(s: str) -> bytes:
    return base64.b64decode(s.encode())

def x25519_keypair():
    private = x25519.X25519PrivateKey.generate()
    public = private.public_key()
    return private, public

def x25519_public_bytes(public):
    return public.public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )

def x25519_private_bytes(private):
    return private.private_bytes(
        serialization.Encoding.Raw,
        serialization.PrivateFormat.Raw,
        serialization.NoEncryption(),
    )

def x25519_private_from_bytes(raw):
    return x25519.X25519PrivateKey.from_private_bytes(raw)

def x25519_public_from_bytes(raw):
    return x25519.X25519PublicKey.from_public_bytes(raw)

def derive_aes_key(secret: bytes, salt: bytes, info: bytes = b"pqci-hybrid-aes-256-gcm") -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=info,
    ).derive(secret)

def aes_encrypt(key: bytes, plaintext: bytes, aad: bytes):
    nonce = __import__("secrets").token_bytes(12)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, aad)
    return nonce, ciphertext

def aes_decrypt(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes):
    return AESGCM(key).decrypt(nonce, ciphertext, aad)

def ed25519_keypair():
    private = ed25519.Ed25519PrivateKey.generate()
    return private, private.public_key()

def ed25519_private_bytes(private):
    return private.private_bytes(
        serialization.Encoding.Raw,
        serialization.PrivateFormat.Raw,
        serialization.NoEncryption(),
    )

def ed25519_public_bytes(public):
    return public.public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )

def ed25519_private_from_bytes(raw):
    return ed25519.Ed25519PrivateKey.from_private_bytes(raw)

def ed25519_public_from_bytes(raw):
    return ed25519.Ed25519PublicKey.from_public_bytes(raw)
