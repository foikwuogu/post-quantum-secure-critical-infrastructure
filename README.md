# Post-Quantum Secure Critical Infrastructure

An independent research prototype aligned with the paper:

**Quantum-Resilient Infrastructure: Migrating US Financial Payment System to Post-Quantum Cryptography (PQC) Standards to Prevent "Harvest Now, Decrypt Later" Attacks**

The paper proposes a phased migration centered on NIST-standardized PQC, hybrid cryptographic wrappers, dual signatures, cryptographic agility, message-size/latency evaluation, and quantum-readiness assessment.

This repository turns those concepts into a runnable local laboratory and extends the application domain from financial-payment infrastructure to a **synthetic critical-energy infrastructure environment**.

> **Important:** This project is an independent simulation. It does not connect to, scan, monitor, or use proprietary data from Energy Transfer, Marathon Petroleum, ExxonMobil, any utility, pipeline, refinery, SCADA system, payment network, bank, or other real critical infrastructure.

## What the project demonstrates

1. **Classical baseline**
   - X25519 key agreement
   - Ed25519 signatures
   - AES-256-GCM payload encryption

2. **Post-quantum mode**
   - NIST FIPS 203 ML-KEM-768 for key establishment
   - NIST FIPS 204 ML-DSA-65 for signatures
   - AES-256-GCM for symmetric encryption

3. **Hybrid mode**
   - X25519 + ML-KEM-768
   - HKDF-SHA-256 over both shared secrets
   - AES-256-GCM
   - Dual signatures: Ed25519 + ML-DSA-65
   - Verification requires both signatures in strict mode

4. **Migration inventory**
   - synthetic assets
   - cryptographic algorithms
   - data sensitivity
   - secrecy lifetime
   - migration complexity
   - quantum-risk score

5. **Performance laboratory**
   - key-establishment latency
   - signature generation latency
   - verification latency
   - ciphertext/package size
   - throughput estimates from measured local runs

6. **Cryptographic agility**
   - algorithm choices are configuration-driven
   - migration policies can select classical, PQC, or hybrid modes
   - the application layer does not hard-code one cryptographic primitive

## Alignment with the source paper

The source paper focuses on FedWire, CHIPS, ACH/RTP, ISO 20022, HNDL, ML-KEM, ML-DSA, SLH-DSA, hybrid key exchange, dual signatures, cryptographic agility, hardware/latency constraints, and phased migration.

The implementation maps those ideas as follows:

| Paper concept | Project implementation |
|---|---|
| HNDL | threat model + secrecy-lifetime risk scoring |
| ML-KEM | real ML-KEM-768 via OpenSSL 3.5 |
| ML-DSA | real ML-DSA-65 via OpenSSL 3.5 |
| Hybrid KEM | X25519 + ML-KEM-768 + HKDF |
| Dual signature | Ed25519 + ML-DSA-65 |
| Cryptographic agility | `crypto/config.py` |
| ISO 20022-style message | synthetic payment/critical-operation envelope |
| Packet/message bloat | measured envelope sizes |
| Latency trade-off | benchmark API and CLI |
| Migration roadmap | inventory + risk score + phases |
| Quantum readiness | asset-level readiness score |

## Important source-alignment note

The paper was published in 2024. NIST's finalized PQC standards are now FIPS 203, FIPS 204 and FIPS 205. NIST finalized ML-KEM, ML-DSA and SLH-DSA on August 13, 2024. This project therefore uses the **final NIST names**, not the draft-era names Kyber/Dilithium as primary API labels.

NIST describes FIPS 203 ML-KEM as a key-encapsulation mechanism and specifies ML-KEM-512, ML-KEM-768 and ML-KEM-1024. FIPS 204 specifies ML-DSA for digital signatures. FIPS 205 specifies SLH-DSA as a stateless hash-based signature scheme.

## Why OpenSSL 3.5?

To keep the project locally reproducible without requiring a specialized PQC Python package or a system-wide liboqs installation, the PQC operations are performed through the OpenSSL command line.

The project expects an OpenSSL version that exposes:

```text
ML-KEM-768
ML-DSA-65
```

Check:

```bash
openssl version
openssl list -kem-algorithms
openssl list -signature-algorithms
```

OpenSSL 3.5 or later is recommended.

## Architecture

```text
                    ┌──────────────────────────┐
                    │      Web Dashboard       │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │        FastAPI API       │
                    └─────┬──────────┬─────────┘
                          │          │
                 ┌────────▼───┐  ┌──▼────────────┐
                 │ Migration  │  │ Crypto Service │
                 │ Risk Engine│  │                │
                 └────────────┘  │ Classical      │
                                  │ PQC            │
                                  │ Hybrid         │
                                  └──────┬─────────┘
                                         │
                     ┌───────────────────┼──────────────────┐
                     │                   │                  │
                 X25519              ML-KEM-768         ML-DSA-65
                 Ed25519             FIPS 203           FIPS 204
                     │                   │                  │
                     └──────────┬────────┴──────────┬───────┘
                                │                   │
                           HKDF-SHA256          Dual Verify
                                │                   │
                           AES-256-GCM          Envelope
```

## Project layout

```text
post-quantum-secure-critical-infrastructure/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── seed.py
│   ├── migration.py
│   ├── service.py
│   ├── crypto/
│   │   ├── classical.py
│   │   ├── openssl_pqc.py
│   │   ├── hybrid.py
│   │   ├── envelope.py
│   │   └── config.py
│   └── static/
├── tests/
├── docs/
├── scripts/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── run.py
```

## Run locally in VS Code

### Prerequisites

- Python 3.11+
- OpenSSL 3.5+
- Git
- VS Code

### Verify OpenSSL

```bash
openssl version
openssl list -kem-algorithms
openssl list -signature-algorithms
```

You should see `ML-KEM-768` and `ML-DSA-65`.

### Create environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Test:

```bash
python -m pytest -q
```

Run:

```bash
python run.py
```

Open:

- Dashboard: http://127.0.0.1:8001/
- API docs: http://127.0.0.1:8001/docs

## CLI benchmark

After starting the application, run:

```bash
python scripts/benchmark.py
```

Or directly:

```bash
python scripts/benchmark.py --iterations 5
```

The benchmark reports measured values from the local machine. Do not copy these numbers into a paper or NIW petition unless you actually ran the benchmark and document the environment.

## Docker

Docker must have OpenSSL 3.5+ available in the container. The included Dockerfile uses a modern Ubuntu base and installs OpenSSL from the Ubuntu repositories available to that image.

```bash
docker compose up --build
```

Open:

http://127.0.0.1:8001/

### Grafana monitoring

The Docker Compose stack also provisions Prometheus and Grafana. Start the full
stack with:

```bash
docker-compose up --build
```

Open Grafana at http://127.0.0.1:3001/ and select the **PQC Infrastructure
Overview** dashboard. The default local login is `admin` / `admin`.

The dashboard displays total assets, high-risk assets, average risk,
readiness, asset-level risk scores, and ML-KEM/ML-DSA availability. Prometheus
scrapes the application metrics at `/metrics`.

## API

### Health

`GET /api/health`

### Inventory

`GET /api/inventory`

### Migration assessment

`GET /api/migration/assessment`

### Crypto capabilities

`GET /api/crypto/capabilities`

### Create encrypted envelope

`POST /api/crypto/encrypt`

```json
{
  "mode": "hybrid",
  "message": {
    "message_id": "OP-0001",
    "message_type": "critical-operation",
    "sender": "NODE-A",
    "receiver": "NODE-B",
    "amount": 125000,
    "currency": "USD",
    "timestamp": "2026-08-19T20:00:00Z"
  }
}
```

### Decrypt envelope

`POST /api/crypto/decrypt`

Pass the returned envelope.

### Sign envelope

`POST /api/crypto/sign`

### Verify envelope

`POST /api/crypto/verify`

### Benchmark

`POST /api/benchmark`

## Research experiments

### Experiment 1 — Cryptographic overhead

Compare:

- classical
- PQC
- hybrid

Measure:

- key establishment time
- signature generation
- signature verification
- encrypted package size
- signature size
- KEM ciphertext size

### Experiment 2 — HNDL migration pressure

Vary:

- data secrecy lifetime
- estimated migration duration
- estimated quantum-advantage horizon

Calculate a transparent risk score.

### Experiment 3 — Hybrid migration

Compare:

```text
Classical only
      vs
PQC only
      vs
Hybrid
```

Evaluate:

- compatibility
- security assumptions
- latency
- message size
- operational migration stage

### Experiment 4 — Cryptographic agility

Change the configured algorithm without changing application business logic.

## Research integrity

This repository contains **measured software behavior**, not claims about real payment networks or real critical infrastructure.

Do not claim:

- deployment at a utility
- deployment at a bank
- FedWire/CHIPS access
- real SCADA integration
- real financial transaction processing
- real-world attack prevention

unless independently documented and authorized.

## License

MIT
