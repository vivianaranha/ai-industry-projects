"""Development launcher for the FastAPI backend."""
from pathlib import Path
import sys
import uvicorn

# Add the standalone project root so `backend` is importable on every OS.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == "__main__":
    # reload=True is useful during development; disable it for production.
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
