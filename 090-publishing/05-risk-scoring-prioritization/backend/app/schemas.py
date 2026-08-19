"""Pydantic request/response contracts shared by the API endpoints."""
from typing import Any
from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    # Free-form text supports NLP/RAG/document projects.
    text: str = Field(default="", max_length=20000)
    # Numeric features support forecasting, risk, anomaly, and optimization projects.
    features: dict[str, float] = Field(default_factory=dict)
    # Options are intentionally flexible for experimentation from the UI/API.
    options: dict[str, Any] = Field(default_factory=dict)


class InferenceResponse(BaseModel):
    request_id: int
    task_type: str
    result: dict[str, Any]
