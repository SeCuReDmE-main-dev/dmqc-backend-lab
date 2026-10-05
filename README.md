# DMQC Backend Lab

A bounded Python backend for reproducible scientific evaluation. The first release prepares an authenticated Render API and an exact statistical confidence-bound calculation. Remote jobs, database access, microscopy inference, and scientific qualification are not implemented in this API yet.

The direction separates explicit code and validation, bounded decisions with replaceable classifiers, and visual or generative interpretation when needed. YOLO is a perception candidate; Jev is optional. Contributions require independent evaluation.

## Scientific attribution

The original DMQC work is **Stefano Curtarolo, Dane Morgan, Kristin Persson, John Rodgers and Gerbrand Ceder, “Predicting Crystal Structures with Data Mining of Quantum Calculations,” Physical Review Letters 91, 135503 (2003)**: https://doi.org/10.1103/PhysRevLett.91.135503.

This project does not reproduce that paper's quantum-calculation method or claim authorship of it. No quantum advantage, drug-discovery efficacy, universal 98% correctness, or superiority of a model combination is claimed.

## API

| Route | Access | Purpose |
|---|---|---|
| GET /healthz | Public | Process health without private information. |
| GET /readyz | Bearer token | Reports implemented API readiness; jobs disabled, database disconnected. |
| POST /v1/bounds | Bearer token | Exact one-sided 95% binomial lower bound with Bonferroni correction. |

Send JSON with integer successes, total and optional comparisons (default 1). Limits: 0 <= successes <= total <= 10000000, positive total, comparisons between 1 and 1000. Request bodies are limited to 8192 bytes. Qualification is always not_assessed. Statistical interpretation requires independent Bernoulli cases and a declared protocol; the numeric bound does not replace physical validation or independent review.

## Local verification

Use Python 3.13.7 and a dedicated virtual environment:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r profiles/render-requirements.txt
.venv/Scripts/python.exe -m unittest discover -s tests -p test_render_app.py -v
.venv/Scripts/python.exe -m unittest discover -s tests -p test_reference.py -v
```

The published tests contain ten cases. Additional private research tools and datasets are outside this release. Gunicorn runs on Linux.

## Render configuration

render.yaml defines one Python web service in Ohio on the 1c-2g plan (1 CPU, 2 GB RAM), selected at 25 USD/month in the dashboard on October 5, 2026. Database, disk and worker services are not provisioned. Automatic deployments are off; initial creation still deploys. The Blueprint generates a dedicated DMQC_API_TOKEN. Protected requests fail closed when authentication is not configured. Manual Web Service setup needs separate configuration of this dedicated token; it does not apply Blueprint environment generation automatically. Research-provider keys are not needed by the currently implemented API.

Build command:

```text
pip install -r profiles/render-requirements.txt
```

Start command:

```sh
gunicorn dmqc_lab.render_app:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 30 --access-logfile -
```

Health check path: /healthz. Compute and other usage are billable; promotional credits do not define a guaranteed shutdown date. Review usage before credits are exhausted. A remote service cannot reach a workstation database at 127.0.0.1.

References: https://render.com/docs/blueprint-spec and https://render.com/docs/free.

## Release boundaries

Credentials, private notes, datasets, billing information, SQL seeds and private execution records are excluded. Never put tokens in URLs or Git history. This is not a contest submission. Dataset and model licenses need review before incorporating them into later releases. No open-source license grant is specified yet.
