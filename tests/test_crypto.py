from app.crypto.envelope import encrypt, decrypt, sign_envelope, verify_envelope
from app.crypto.openssl_pqc import capabilities

MESSAGE = {
    "message_id": "TEST-001",
    "message_type": "critical-operation",
    "sender": "NODE-A",
    "receiver": "NODE-B",
    "amount": 1000.0,
    "currency": "USD",
    "timestamp": "2026-08-19T20:00:00Z",
}

def test_openssl_pqc_capabilities():
    caps = capabilities()
    assert caps["ml_kem_768"] is True
    assert caps["ml_dsa_65"] is True

def test_classical_round_trip():
    env = encrypt("classical", MESSAGE)
    assert decrypt(env) == MESSAGE

def test_pqc_round_trip():
    env = encrypt("pqc", MESSAGE)
    assert decrypt(env) == MESSAGE

def test_hybrid_round_trip():
    env = encrypt("hybrid", MESSAGE)
    assert decrypt(env) == MESSAGE

def test_hybrid_dual_signature():
    env = encrypt("hybrid", MESSAGE)
    signed = sign_envelope(env, "hybrid")
    result = verify_envelope(signed)
    assert result["valid"] is True
    assert result["checks"]["ed25519"] is True
    assert result["checks"]["ml_dsa_65"] is True

def test_tampered_signature_fails():
    env = encrypt("hybrid", MESSAGE)
    signed = sign_envelope(env, "hybrid")
    signed["ciphertext"] = signed["ciphertext"][:-2] + "AA"
    result = verify_envelope(signed)
    assert result["valid"] is False
