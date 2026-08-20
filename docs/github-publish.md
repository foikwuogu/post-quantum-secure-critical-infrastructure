# Publish to GitHub

Create a new empty repository, then from the project root:

```bash
git init
git add .
git commit -m "Initial post-quantum critical infrastructure laboratory"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/post-quantum-secure-critical-infrastructure.git
git push -u origin main
```

Before publishing:

```bash
python -m pytest -q
```

Do not commit:

- `.venv`
- database files
- private keys
- proprietary logs
- company network diagrams
- customer information
- production credentials
- real OT/SCADA configuration
- unpublished research data
