import json
import statistics
import time
from sqlalchemy import select
from sqlalchemy.orm import Session
from .crypto.envelope import encrypt, decrypt, sign_envelope, verify_envelope
from .crypto.openssl_pqc import capabilities
from .migration import assess_all
from .models import Asset, BenchmarkRun

def inventory(db):
    assets = assess_all(db)
    return [
        {
            "id": a.id,
            "asset_name": a.asset_name,
            "sector": a.sector,
            "zone": a.zone,
            "current_algorithm": a.current_algorithm,
            "key_exchange": a.key_exchange,
            "signature_algorithm": a.signature_algorithm,
            "data_classification": a.data_classification,
            "secrecy_years": a.secrecy_years,
            "migration_months": a.migration_months,
            "criticality": a.criticality,
            "quantum_risk_score": a.quantum_risk_score,
            "readiness_score": a.readiness_score,
        }
        for a in assets
    ]

def run_benchmark(db: Session, iterations: int):
    message = {
        "message_id": "BENCH-001",
        "message_type": "critical-operation",
        "sender": "NODE-A",
        "receiver": "NODE-B",
        "amount": 125000.0,
        "currency": "USD",
        "timestamp": "2026-08-19T20:00:00Z",
    }
    rows = []

    for mode in ["classical", "pqc", "hybrid"]:
        enc_times = []
        sign_times = []
        sizes = []

        for _ in range(iterations):
            t0 = time.perf_counter()
            env = encrypt(mode, message)
            enc_times.append((time.perf_counter() - t0) * 1000)

            t0 = time.perf_counter()
            signed = sign_envelope(env, mode)
            sign_times.append((time.perf_counter() - t0) * 1000)
            sizes.append(len(json.dumps(signed, separators=(",", ":")).encode()))

            # Round-trip verifies the actual cryptographic path.
            assert decrypt(env) == message
            assert verify_envelope(signed)["valid"] is True

        for operation, values in [
            ("encryption", enc_times),
            ("signing", sign_times),
        ]:
            row = BenchmarkRun(
                mode=mode,
                operation=operation,
                iterations=iterations,
                mean_ms=round(statistics.mean(values), 4),
                min_ms=round(min(values), 4),
                max_ms=round(max(values), 4),
                output_bytes=max(sizes),
            )
            db.add(row)
            rows.append({
                "mode": mode,
                "operation": operation,
                "iterations": iterations,
                "mean_ms": row.mean_ms,
                "min_ms": row.min_ms,
                "max_ms": row.max_ms,
                "output_bytes": row.output_bytes,
            })

    db.commit()
    return {
        "openssl": capabilities(),
        "iterations": iterations,
        "results": rows,
    }
