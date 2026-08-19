from fastapi.testclient import TestClient
from backend.app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_predict_returns_result():
    with TestClient(app) as client:
        response = client.post("/predict", json={"text": "sample urgent request", "features": {"x1": 1, "x2": 2, "x3": 3}, "options": {"horizon": 3}})
        assert response.status_code == 200
        body = response.json()
        assert body["request_id"] >= 1
        assert isinstance(body["result"], dict)
