# Research Methodology

## Research question

How does a phased classical-to-PQC migration affect cryptographic security posture, message size, signing/verification latency, and operational migration risk in a synthetic critical-infrastructure environment?

## Hypotheses

H1: PQC and hybrid envelopes will increase cryptographic material and total message size relative to a classical baseline.

H2: Hybrid cryptography will provide a migration path that preserves a classical security component while adding a PQC component.

H3: Assets with longer secrecy lifetimes, higher criticality, and longer migration durations will receive higher quantum-risk scores under the model.

## Independent variables

- cryptographic mode
- ML-KEM parameter set (future extension)
- signature algorithm
- secrecy lifetime
- migration duration
- criticality

## Dependent variables

- encryption time
- signing time
- verification time
- envelope size
- KEM ciphertext size
- signature size
- migration risk score
- readiness score

## Controls

All cryptographic comparisons should use:

- same machine
- same OS
- same OpenSSL version
- same Python version
- same message
- same number of iterations
- same measurement method

## Reproducibility

Record:

```text
OS:
Python:
OpenSSL:
CPU:
RAM:
Iterations:
Message size:
```

Never report benchmark numbers without this context.
