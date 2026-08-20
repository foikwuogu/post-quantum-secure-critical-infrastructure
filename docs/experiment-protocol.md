# Experimental Protocol

## Purpose

Generate reproducible measurements for the comparison of classical, PQC and hybrid cryptographic profiles.

## Test conditions

Record before each published experiment:

- CPU model
- RAM
- OS and version
- Python version
- OpenSSL version
- project commit SHA
- message plaintext size
- iteration count
- warm-up policy

## Procedure

1. Start the application.
2. Confirm `/api/crypto/capabilities` reports ML-KEM-768 and ML-DSA-65.
3. Run the benchmark with at least 30 iterations for research reporting.
4. Repeat the benchmark three times.
5. Record mean, median, standard deviation, minimum and maximum.
6. Record envelope size and individual cryptographic artifact sizes.
7. Preserve raw JSON output.
8. Report hardware/software conditions alongside results.

## Comparisons

### Baseline
X25519 + AES-256-GCM + Ed25519.

### PQC
ML-KEM-768 + AES-256-GCM + ML-DSA-65.

### Hybrid
X25519 + ML-KEM-768 + HKDF-SHA-256 + AES-256-GCM + Ed25519/ML-DSA-65.

## Research caution

A local benchmark demonstrates implementation behavior on the test machine. It does not establish universal performance, security, FIPS validation, or production suitability.
