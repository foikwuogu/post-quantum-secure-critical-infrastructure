from app.database import Base, engine, SessionLocal
from app.seed import seed_assets
from app.migration import assess_all

Base.metadata.create_all(bind=engine)

def test_migration_inventory_has_assets():
    db = SessionLocal()
    try:
        seed_assets(db)
        assets = assess_all(db)
        assert len(assets) >= 4
        assert all(0 <= a.quantum_risk_score <= 100 for a in assets)
        assert all(0 <= a.readiness_score <= 100 for a in assets)
    finally:
        db.close()
