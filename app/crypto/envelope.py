import base64
import json
import os
from datetime import datetime, timezone
from .classical import (
    aes_decrypt, aes_encrypt, b64, derive_aes_key, ed25519_keypair,
    ed25519_private_from_bytes, ed25519_public_bytes, ed25519_public_from_bytes,
    ed25519_private_bytes, x25519_keypair, x25519_private_from_bytes,
    x25519_private_bytes, x25519_public_bytes, x25519_public_from_bytes
)
from .openssl_pqc import (
    mlkem_decapsulate, mlkem_encapsulate, mlkem_keypair,
    mldsa_keypair, mldsa_sign, mldsa_verify
)

class KeyStore:
    def __init__(self):
        self.x_priv, self.x_pub = x25519_keypair()
        self.dsa_priv, self.dsa_pub = ed25519_keypair()
        self.pqc_error = None
        try:
            self.kem_priv, self.kem_pub = mlkem_keypair()
            self.pqc_sig_priv, self.pqc_sig_pub = mldsa_keypair()
        except RuntimeError as exc:
            self.kem_priv = self.kem_pub = None
            self.pqc_sig_priv = self.pqc_sig_pub = None
            self.pqc_error = str(exc)

    def require_pqc(self):
        if self.pqc_error:
            raise RuntimeError(f"PQC is unavailable: {self.pqc_error}")

    def public_material(self):
        return {
            "x25519_public": b64(x25519_public_bytes(self.x_pub)),
            "ed25519_public": b64(ed25519_public_bytes(self.dsa_pub)),
            "ml_kem_public_pem": b64(self.kem_pub) if self.kem_pub else None,
            "ml_dsa_public_pem": b64(self.pqc_sig_pub) if self.pqc_sig_pub else None,
        }

keystore = KeyStore()

def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()

def _encrypt_classical(message):
    eph_priv, eph_pub = x25519_keypair()
    shared = eph_priv.exchange(keystore.x_pub)
    salt = os.urandom(16)
    key = derive_aes_key(shared, salt, b"pqci-classical")
    aad = b"pqci-classical-envelope-v1"
    nonce, ciphertext = aes_encrypt(key, canonical(message), aad)
    return {
        "version": 1,
        "mode": "classical",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "aad": b64(aad),
        "salt": b64(salt),
        "nonce": b64(nonce),
        "ciphertext": b64(ciphertext),
        "ephemeral_x25519_public": b64(x25519_public_bytes(eph_pub)),
        "recipient": "local-demo-node",
    }

def _encrypt_pqc(message):
    keystore.require_pqc()
    ciphertext_kem, pq_secret = mlkem_encapsulate(keystore.kem_pub)
    salt = os.urandom(16)
    key = derive_aes_key(pq_secret, salt, b"pqci-pqc")
    aad = b"pqci-pqc-envelope-v1"
    nonce, ciphertext = aes_encrypt(key, canonical(message), aad)
    return {
        "version": 1,
        "mode": "pqc",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "aad": b64(aad),
        "salt": b64(salt),
        "nonce": b64(nonce),
        "ciphertext": b64(ciphertext),
        "ml_kem_ciphertext": b64(ciphertext_kem),
        "recipient": "local-demo-node",
    }

def _encrypt_hybrid(message):
    keystore.require_pqc()
    eph_priv, eph_pub = x25519_keypair()
    classical_secret = eph_priv.exchange(keystore.x_pub)
    kem_ciphertext, pq_secret = mlkem_encapsulate(keystore.kem_pub)
    salt = os.urandom(16)
    combined = classical_secret + pq_secret
    key = derive_aes_key(combined, salt, b"pqci-hybrid-x25519-mlkem768")
    aad = b"pqci-hybrid-envelope-v1"
    nonce, ciphertext = aes_encrypt(key, canonical(message), aad)
    return {
        "version": 1,
        "mode": "hybrid",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "aad": b64(aad),
        "salt": b64(salt),
        "nonce": b64(nonce),
        "ciphertext": b64(ciphertext),
        "ephemeral_x25519_public": b64(x25519_public_bytes(eph_pub)),
        "ml_kem_ciphertext": b64(kem_ciphertext),
        "recipient": "local-demo-node",
    }

def encrypt(mode, message):
    if mode == "classical":
        return _encrypt_classical(message)
    if mode == "pqc":
        return _encrypt_pqc(message)
    if mode == "hybrid":
        return _encrypt_hybrid(message)
    raise ValueError("Unsupported encryption mode")

def decrypt(envelope):
    mode = envelope["mode"]
    aad = base64.b64decode(envelope["aad"])
    salt = base64.b64decode(envelope["salt"])
    nonce = base64.b64decode(envelope["nonce"])
    ciphertext = base64.b64decode(envelope["ciphertext"])

    if mode == "classical":
        eph_pub = x25519_public_from_bytes(base64.b64decode(envelope["ephemeral_x25519_public"]))
        shared = keystore.x_priv.exchange(eph_pub)
        key = derive_aes_key(shared, salt, b"pqci-classical")
    elif mode == "pqc":
        keystore.require_pqc()
        pq_secret = mlkem_decapsulate(
            keystore.kem_priv,
            base64.b64decode(envelope["ml_kem_ciphertext"])
        )
        key = derive_aes_key(pq_secret, salt, b"pqci-pqc")
    elif mode == "hybrid":
        keystore.require_pqc()
        eph_pub = x25519_public_from_bytes(base64.b64decode(envelope["ephemeral_x25519_public"]))
        classical_secret = keystore.x_priv.exchange(eph_pub)
        pq_secret = mlkem_decapsulate(
            keystore.kem_priv,
            base64.b64decode(envelope["ml_kem_ciphertext"])
        )
        key = derive_aes_key(classical_secret + pq_secret, salt, b"pqci-hybrid-x25519-mlkem768")
    else:
        raise ValueError("Unsupported mode")

    return json.loads(aes_decrypt(key, nonce, ciphertext, aad))

def sign_envelope(envelope, mode):
    payload = canonical(envelope)
    result = dict(envelope)
    result["signatures"] = {}

    if mode in {"classical", "hybrid"}:
        result["signatures"]["ed25519"] = b64(keystore.dsa_priv.sign(payload))

    if mode in {"pqc", "hybrid"}:
        keystore.require_pqc()
        result["signatures"]["ml_dsa_65"] = b64(mldsa_sign(keystore.pqc_sig_priv, payload))

    result["signing_profile"] = mode
    return result

def verify_envelope(signed):
    signatures = signed.get("signatures", {})
    unsigned = dict(signed)
    unsigned.pop("signatures", None)
    unsigned.pop("signing_profile", None)
    payload = canonical(unsigned)
    checks = {}

    if "ed25519" in signatures:
        try:
            keystore.dsa_pub.verify(
                base64.b64decode(signatures["ed25519"]), payload
            )
            checks["ed25519"] = True
        except Exception:
            checks["ed25519"] = False

    if "ml_dsa_65" in signatures:
        keystore.require_pqc()
        checks["ml_dsa_65"] = mldsa_verify(
            keystore.pqc_sig_pub,
            payload,
            base64.b64decode(signatures["ml_dsa_65"])
        )

    profile = signed.get("signing_profile", "classical")
    if profile == "hybrid":
        valid = checks.get("ed25519") is True and checks.get("ml_dsa_65") is True
    elif profile == "pqc":
        valid = checks.get("ml_dsa_65") is True
    else:
        valid = checks.get("ed25519") is True

    return {"valid": valid, "checks": checks, "profile": profile}
