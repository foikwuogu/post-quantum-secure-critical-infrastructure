from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import PlainTextResponse
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
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest

inventory_assets = Gauge("pqc_inventory_assets_total", "Total synthetic infrastructure assets")
inventory_high_risk = Gauge("pqc_inventory_high_risk_assets", "Assets with quantum risk score at least 70")
inventory_average_risk = Gauge("pqc_inventory_average_risk_score", "Average asset quantum risk score")
inventory_average_readiness = Gauge("pqc_inventory_average_readiness_score", "Average asset readiness score")
capability_available = Gauge(
    "pqc_capability_available",
    "Whether a cryptographic capability is available",
    ["capability"],
)
asset_quantum_risk = Gauge(
    "pqc_asset_quantum_risk_score",
    "Quantum risk score by asset",
    ["asset"],
)
asset_readiness = Gauge(
    "pqc_asset_readiness_score",
    "Readiness score by asset",
    ["asset"],
)

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

@app.get("/metrics", response_class=PlainTextResponse, include_in_schema=False)
def metrics():
    db = SessionLocal()
    try:
        assets = inventory(db)
    finally:
        db.close()

    inventory_assets.set(len(assets))
    inventory_high_risk.set(sum(a["quantum_risk_score"] >= 70 for a in assets))
    inventory_average_risk.set(sum(a["quantum_risk_score"] for a in assets) / len(assets))
    inventory_average_readiness.set(sum(a["readiness_score"] for a in assets) / len(assets))

    caps = capabilities()
    capability_available.labels("ml_kem_768").set(caps["ml_kem_768"])
    capability_available.labels("ml_dsa_65").set(caps["ml_dsa_65"])
    for asset in assets:
        asset_quantum_risk.labels(asset["asset_name"]).set(asset["quantum_risk_score"])
        asset_readiness.labels(asset["asset_name"]).set(asset["readiness_score"])

    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

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
