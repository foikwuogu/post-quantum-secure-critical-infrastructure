import base64
import subprocess
import tempfile
from pathlib import Path
from .config import PROFILES
from ..config import OPENSSL_BIN

def _run(args, input_bytes=None):
    result = subprocess.run(
        [OPENSSL_BIN] + args,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"OpenSSL command failed ({result.returncode}): "
            + result.stderr.decode(errors="replace")
        )
    return result.stdout

def openssl_version():
    return _run(["version"]).decode().strip()

def capabilities():
    kem = _run(["list", "-kem-algorithms"]).decode(errors="replace")
    sig = _run(["list", "-signature-algorithms"]).decode(errors="replace")
    return {
        "openssl": openssl_version(),
        "ml_kem_768": "ML-KEM-768" in kem or "MLKEM768" in kem,
        "ml_dsa_65": "ML-DSA-65" in sig or "MLDSA65" in sig,
    }

def _write(path: Path, data: bytes):
    path.write_bytes(data)

def _read(path: Path):
    return path.read_bytes()

def mlkem_keypair():
    with tempfile.TemporaryDirectory(prefix="pqci-kem-") as td:
        td = Path(td)
        priv = td / "priv.pem"
        pub = td / "pub.pem"
        _run(["genpkey", "-algorithm", "ML-KEM-768", "-out", str(priv)])
        _run(["pkey", "-in", str(priv), "-pubout", "-out", str(pub)])
        return _read(priv), _read(pub)

def mlkem_encapsulate(public_pem: bytes):
    with tempfile.TemporaryDirectory(prefix="pqci-encap-") as td:
        td = Path(td)
        pub = td / "pub.pem"
        ct = td / "ct.bin"
        secret = td / "secret.bin"
        _write(pub, public_pem)
        _run([
            "pkeyutl", "-encap", "-pubin", "-inkey", str(pub),
            "-out", str(ct), "-secret", str(secret)
        ])
        return _read(ct), _read(secret)

def mlkem_decapsulate(private_pem: bytes, ciphertext: bytes):
    with tempfile.TemporaryDirectory(prefix="pqci-decap-") as td:
        td = Path(td)
        priv = td / "priv.pem"
        ct = td / "ct.bin"
        secret = td / "secret.bin"
        _write(priv, private_pem)
        _write(ct, ciphertext)
        _run([
            "pkeyutl", "-decap", "-inkey", str(priv),
            "-in", str(ct), "-secret", str(secret)
        ])
        return _read(secret)

def mldsa_keypair():
    with tempfile.TemporaryDirectory(prefix="pqci-dsa-") as td:
        td = Path(td)
        priv = td / "priv.pem"
        pub = td / "pub.pem"
        _run(["genpkey", "-algorithm", "ML-DSA-65", "-out", str(priv)])
        _run(["pkey", "-in", str(priv), "-pubout", "-out", str(pub)])
        return _read(priv), _read(pub)

def mldsa_sign(private_pem: bytes, message: bytes):
    with tempfile.TemporaryDirectory(prefix="pqci-sign-") as td:
        td = Path(td)
        priv = td / "priv.pem"
        msg = td / "msg.bin"
        sig = td / "sig.bin"
        _write(priv, private_pem)
        _write(msg, message)
        _run(["pkeyutl", "-sign", "-inkey", str(priv), "-in", str(msg), "-out", str(sig)])
        return _read(sig)

def mldsa_verify(public_pem: bytes, message: bytes, signature: bytes):
    with tempfile.TemporaryDirectory(prefix="pqci-verify-") as td:
        td = Path(td)
        pub = td / "pub.pem"
        msg = td / "msg.bin"
        sig = td / "sig.bin"
        _write(pub, public_pem)
        _write(msg, message)
        _write(sig, signature)
        result = subprocess.run(
            [OPENSSL_BIN, "pkeyutl", "-verify", "-pubin",
             "-inkey", str(pub), "-in", str(msg), "-sigfile", str(sig)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        return result.returncode == 0
