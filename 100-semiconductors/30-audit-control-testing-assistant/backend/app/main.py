"""FastAPI entry point for this end-to-end AI use case."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .config import settings
from .database import initialize_database, list_history, save_inference
from .schemas import InferenceRequest, InferenceResponse
from .services.ai_service import UseCaseEngine

engine = UseCaseEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize persistent storage once when the service starts.
    initialize_database()
    yield

app = FastAPI(title=settings.project_name, version="1.0.0", lifespan=lifespan)

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "industry": settings.industry, "use_case": settings.use_case}

@app.get("/metadata")
def metadata() -> dict:
    return {"project_name": settings.project_name, "industry": settings.industry, "use_case": settings.use_case, "task_type": settings.task_type}

@app.post("/predict", response_model=InferenceResponse)
def predict(payload: InferenceRequest) -> InferenceResponse:
    # The engine returns a plain dictionary so the project can easily swap in a
    # different model or external service without changing the API contract.
    result = engine.run(payload.text, payload.features, payload.options)
    request_id = save_inference(payload.model_dump(), result)
    return InferenceResponse(request_id=request_id, task_type=settings.task_type, result=result)

@app.get("/history")
def history(limit: int = 20) -> list[dict]:
    return list_history(max(1, min(limit, 100)))
