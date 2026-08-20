from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import APP_NAME, APP_VERSION
from .database import Base, SessionLocal, engine, get_db
from .models import Asset, BenchmarkRun
from .schemas import BenchmarkRequest, EncryptRequest, EnvelopeRequest
from .seed import seed_assets
from .service import inventory, run_benchmark
from .crypto.envelope import decrypt, encrypt, sign_envelope, verify_envelope
from .crypto.openssl_pqc import capabilities, openssl_version

Base.metadata.create_all(bind=engine)

app = FastAPI(title=APP_NAME, version=APP_VERSION)

@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        seed_assets(db)
    finally:
        db.close()

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(Path(__file__).parent / "static" / "index.html")

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": APP_NAME,
        "version": APP_VERSION,
        "openssl": openssl_version(),
    }

@app.get("/api/crypto/capabilities")
def crypto_capabilities():
    return capabilities()

@app.get("/api/inventory")
def get_inventory(db: Session = Depends(get_db)):
    return inventory(db)

@app.get("/api/migration/assessment")
def migration_assessment(db: Session = Depends(get_db)):
    return inventory(db)

@app.get("/api/migration/roadmap")
def migration_roadmap(db: Session = Depends(get_db)):
    assets = inventory(db)
    ordered = sorted(assets, key=lambda a: a["quantum_risk_score"], reverse=True)
    return {
        "phases": [
            {"phase": 1, "name": "Discover", "objective": "Inventory cryptographic dependencies and data lifetimes"},
            {"phase": 2, "name": "Prioritize", "objective": "Rank HNDL exposure and operational criticality"},
            {"phase": 3, "name": "Hybridize", "objective": "Introduce classical + PQC protections"},
            {"phase": 4, "name": "Validate", "objective": "Measure latency, size, interoperability and failure behavior"},
            {"phase": 5, "name": "Transition", "objective": "Retire legacy algorithms where justified"},
        ],
        "priority_assets": ordered[:5],
        "scenario_note": "Risk scores are synthetic research-model outputs, not predictions of a real quantum timeline."
    }

@app.post("/api/crypto/encrypt")
def crypto_encrypt(request: EncryptRequest):
    try:
        return encrypt(request.mode, request.message.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/api/crypto/decrypt")
def crypto_decrypt(request: EnvelopeRequest):
    try:
        return decrypt(request.envelope)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/api/crypto/sign")
def crypto_sign(request: EnvelopeRequest):
    try:
        mode = request.envelope.get("mode", "classical")
        return sign_envelope(request.envelope, mode)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/api/crypto/verify")
def crypto_verify(request: EnvelopeRequest):
    try:
        return verify_envelope(request.envelope)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/api/benchmark")
def benchmark(request: BenchmarkRequest, db: Session = Depends(get_db)):
    try:
        return run_benchmark(db, request.iterations)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/api/benchmarks")
def benchmarks(db: Session = Depends(get_db)):
    rows = db.scalars(select(BenchmarkRun).order_by(BenchmarkRun.id.desc()).limit(100)).all()
    return rows
