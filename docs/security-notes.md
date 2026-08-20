# Security Notes

## What this project is

A controlled local cryptography laboratory.

## What it is not

- a production HSM
- a production PKI
- a banking gateway
- a SCADA controller
- a real payment rail
- a FIPS-validated cryptographic module
- a replacement for professional cryptographic review

## Key handling

Demo keys are generated at application startup and kept in memory. They are not intended for production use.

## OpenSSL

PQC operations use the local OpenSSL binary. The project checks for ML-KEM-768 and ML-DSA-65 before running the PQC tests.

## Hybrid construction

The project uses two independently derived shared secrets and combines them through HKDF before AES-256-GCM encryption. This is a research implementation of the migration concept; it is not a claim that the construction is a standardized TLS hybrid suite.

## Threat model

The project focuses on HNDL-style confidentiality risk and migration engineering. It does not model every quantum or classical attack.
