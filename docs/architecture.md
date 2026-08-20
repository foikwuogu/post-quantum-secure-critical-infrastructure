# System Architecture

```text
                   ┌─────────────────────────┐
                   │ Quantum Readiness UI    │
                   └────────────┬────────────┘
                                │ HTTP/JSON
                   ┌────────────▼────────────┐
                   │ FastAPI API Layer        │
                   └──────┬─────────┬────────┘
                          │         │
              ┌───────────▼───┐ ┌──▼────────────────┐
              │ Migration     │ │ Crypto Service    │
              │ Risk Engine   │ │                   │
              └───────┬───────┘ │ Classical         │
                      │         │ PQC               │
                      │         │ Hybrid            │
                      │         └───────┬───────────┘
                      │                 │
              ┌───────▼───────┐  ┌────▼──────────────┐
              │ SQLite        │  │ OpenSSL 3.5+      │
              │ Asset DB      │  │ ML-KEM / ML-DSA   │
              └───────────────┘  └───────────────────┘
```

## Trust boundaries

1. Browser to API: local development HTTP boundary.
2. API to crypto service: application boundary.
3. Crypto service to OpenSSL process: local process boundary.
4. API to SQLite: local data boundary.

## Data flow

A synthetic critical-operation message is serialized canonically, encrypted using the selected profile, optionally signed, verified, and decrypted. The benchmark records timing and package-size measurements.

## Security posture

The design is deliberately laboratory-oriented. It uses in-memory demo keys and local synthetic data. It is not a production PKI/HSM architecture.
