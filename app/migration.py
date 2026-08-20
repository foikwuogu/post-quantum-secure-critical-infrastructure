from sqlalchemy import select
from .models import Asset

def assess_asset(asset: Asset):
    # Mosca-style timing intuition:
    # secrecy lifetime + migration duration should not approach/exceed the
    # estimated quantum-advantage horizon.
    migration_years = asset.migration_months / 12.0
    quantum_horizon_years = 10.0  # scenario parameter, not a prediction
    exposure_window = asset.secrecy_years + migration_years

    timing_risk = min(100.0, max(0.0, (exposure_window / quantum_horizon_years) * 50))
    criticality_risk = asset.criticality * 0.35

    legacy_penalty = 0
    if any(x in asset.current_algorithm.upper() for x in ["RSA", "ECDSA", "ECDH", "ED25519", "X25519"]):
        legacy_penalty = 20

    risk = min(100.0, round(timing_risk + criticality_risk + legacy_penalty, 2))
    readiness = round(100.0 - risk, 2)

    asset.quantum_risk_score = risk
    asset.readiness_score = readiness
    return asset

def assess_all(db):
    assets = db.scalars(select(Asset).order_by(Asset.id)).all()
    for asset in assets:
        assess_asset(asset)
    db.commit()
    return assets
