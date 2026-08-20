import os
from pathlib import Path

APP_NAME = "Post-Quantum Secure Critical Infrastructure"
APP_VERSION = "1.0.0"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/pqc.db")
OPENSSL_BIN = os.getenv("OPENSSL_BIN", "openssl")
WORK_DIR = Path(os.getenv("PQC_WORK_DIR", "./tmp_crypto"))
WORK_DIR.mkdir(parents=True, exist_ok=True)
