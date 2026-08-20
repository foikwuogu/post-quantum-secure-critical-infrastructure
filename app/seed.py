from sqlalchemy import select
from .models import Asset

def seed_assets(db):
    if db.scalar(select(Asset.id).limit(1)) is not None:
        return

    assets = [
        Asset(
            asset_name="Synthetic Control Gateway A",
            sector="Energy",
            zone="OT",
            current_algorithm="RSA-2048 / ECDSA-P256",
            key_exchange="ECDH-P256",
            signature_algorithm="ECDSA-P256",
            data_classification="Restricted",
            secrecy_years=20,
            migration_months=30,
            criticality=95,
        ),
        Asset(
            asset_name="Synthetic Historian B",
            sector="Energy",
            zone="OT",
            current_algorithm="ECDSA-P256",
            key_exchange="ECDH-P256",
            signature_algorithm="ECDSA-P256",
            data_classification="Confidential",
            secrecy_years=12,
            migration_months=24,
            criticality=85,
        ),
        Asset(
            asset_name="Synthetic Operations API C",
            sector="Energy",
            zone="IT",
            current_algorithm="RSA-3072 / ECDSA-P384",
            key_exchange="ECDH-P384",
            signature_algorithm="ECDSA-P384",
            data_classification="Confidential",
            secrecy_years=8,
            migration_months=18,
            criticality=75,
        ),
        Asset(
            asset_name="Synthetic Engineering Repository D",
            sector="Energy",
            zone="IT",
            current_algorithm="Ed25519",
            key_exchange="X25519",
            signature_algorithm="Ed25519",
            data_classification="Internal",
            secrecy_years=5,
            migration_months=12,
            criticality=60,
        ),
    ]
    db.add_all(assets)
    db.commit()
