from dataclasses import dataclass

@dataclass(frozen=True)
class CryptoProfile:
    name: str
    key_exchange: str
    signature: str
    quantum_resistant: bool
    hybrid: bool

PROFILES = {
    "classical": CryptoProfile(
        name="classical",
        key_exchange="X25519",
        signature="Ed25519",
        quantum_resistant=False,
        hybrid=False,
    ),
    "pqc": CryptoProfile(
        name="pqc",
        key_exchange="ML-KEM-768",
        signature="ML-DSA-65",
        quantum_resistant=True,
        hybrid=False,
    ),
    "hybrid": CryptoProfile(
        name="hybrid",
        key_exchange="X25519 + ML-KEM-768",
        signature="Ed25519 + ML-DSA-65",
        quantum_resistant=True,
        hybrid=True,
    ),
}
