from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.seed import seed_assets

_db = SessionLocal()
seed_assets(_db)
_db.close()
client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_inventory():
    r = client.get("/api/inventory")
    assert r.status_code == 200
    assert len(r.json()) >= 4

def test_encrypt_api():
    payload = {
        "mode":"hybrid",
        "message":{
            "message_id":"API-001",
            "message_type":"critical-operation",
            "sender":"NODE-A",
            "receiver":"NODE-B",
            "amount":100.0,
            "currency":"USD",
            "timestamp":"2026-08-19T20:00:00Z"
        }
    }
    r = client.post("/api/crypto/encrypt", json=payload)
    assert r.status_code == 200
    assert r.json()["mode"] == "hybrid"
