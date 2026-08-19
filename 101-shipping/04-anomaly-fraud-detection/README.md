# Shipping — Anomaly and Fraud Detection

## Business Problem

This project demonstrates how AI can support **shipping operations** by applying **anomaly and fraud detection** to a realistic shipment. The user persona is typically a **shipper** or an employee supporting that workflow.

## What the Application Does

Detect unusual records, suspicious activity, or operational anomalies.

The implementation is deliberately end-to-end: a user interacts with a Streamlit interface, the UI calls a FastAPI service, the backend executes a local AI/ML workflow, the result is persisted to SQLite, and the user receives an auditable response.

## Success Metrics to Define Before Production

- Cycle-time reduction
- Accuracy / precision / retrieval quality appropriate to the task
- Human-review rate
- Exception or failure rate
- User adoption and task completion
- Cost per processed record
- Business outcome specific to Shipping

## Project Structure

```text
04-anomaly-fraud-detection/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   └── services/ai_service.py
│   └── tests/test_api.py
├── frontend/app.py
├── data/
│   ├── training.csv
│   ├── catalog.csv
│   └── knowledge.txt
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── SECURITY_AND_GOVERNANCE.md
├── scripts/
│   ├── run_backend.py
│   └── seed_db.py
├── .env.example
├── requirements.txt
└── README.md
```

## Run It

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize the database

```bash
python scripts/seed_db.py
```

### 4. Start the backend

```bash
python scripts/run_backend.py
```

API documentation is available at `http://127.0.0.1:8000/docs`.

### 5. Start the frontend

Open a second terminal in this project folder and run:

```bash
streamlit run frontend/app.py
```

### 6. Run tests

```bash
pytest backend/tests -q
```

## Optional Ollama

The baseline does not require a hosted API. To enable local generative responses:

1. Copy `.env.example` to `.env`.
2. Set `USE_OLLAMA=true`.
3. Change `OLLAMA_MODEL` if needed.
4. Make sure Ollama is running locally.

If Ollama is unavailable, the application falls back to deterministic local behavior.

## Productionization Ideas

- Replace CSV sample data with approved Shipping data sources.
- Add SSO/RBAC and an API gateway.
- Add data validation, PII/sensitive-data controls, and secrets management.
- Replace the baseline algorithm with a validated domain model where justified.
- Add model/version tracking, evaluation datasets, drift monitoring, and observability.
- Integrate the recommendation/action with the real system of record.
- Add explicit human approval before high-impact actions.
- Define rollback, incident response, and ownership.

See `docs/SECURITY_AND_GOVERNANCE.md` before adapting the demo to real data.
