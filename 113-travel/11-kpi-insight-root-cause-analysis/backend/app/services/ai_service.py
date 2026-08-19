"""Reusable local AI engine.

Each project sets TASK_TYPE in `.env.example`. The engine dispatches to a
small, fully local implementation for that task. This gives every generated
project a working baseline that learners can later replace with enterprise
models, vector databases, feature stores, or external systems.
"""
from __future__ import annotations
from pathlib import Path
import json
import math
import re
from typing import Any

import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity

from ..config import settings


class UseCaseEngine:
    def __init__(self) -> None:
        self.data_dir = Path("data")

    def run(self, text: str, features: dict[str, float], options: dict[str, Any]) -> dict[str, Any]:
        """Dispatch one request to the algorithm that matches this project."""
        handlers = {
            "rag": self._rag,
            "document_intelligence": self._document_intelligence,
            "forecasting": self._forecasting,
            "anomaly_detection": self._anomaly_detection,
            "risk_scoring": self._risk_scoring,
            "recommendation": self._recommendation,
            "optimization": self._optimization,
            "classification": self._classification,
            "support_copilot": self._support_copilot,
            "agentic_workflow": self._agentic_workflow,
            "analytics": self._analytics,
            "compliance": self._compliance,
        }
        handler = handlers.get(settings.task_type, self._classification)
        return handler(text=text, features=features, options=options)

    # ---------- Optional local LLM integration ----------
    def _ollama(self, prompt: str) -> str | None:
        if not settings.use_ollama:
            return None
        try:
            response = requests.post(
                f"{settings.ollama_url}/api/generate",
                json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
                timeout=60,
            )
            response.raise_for_status()
            return response.json().get("response", "").strip() or None
        except Exception:
            # A robust demo should degrade gracefully instead of crashing when the
            # optional model server is unavailable.
            return None

    # ---------- RAG ----------
    def _rag(self, text: str, features: dict, options: dict) -> dict:
        knowledge = (self.data_dir / "knowledge.txt").read_text(encoding="utf-8")
        chunks = [c.strip() for c in knowledge.split("\n\n") if c.strip()]
        query = text.strip() or "What should I know?"
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(chunks + [query])
        scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
        top_idx = scores.argsort()[::-1][:3]
        contexts = [chunks[i] for i in top_idx]
        prompt = (
            f"You are an assistant for {settings.industry}. Answer only from the context.\n"
            f"Question: {query}\nContext:\n" + "\n---\n".join(contexts)
        )
        generated = self._ollama(prompt)
        answer = generated or " ".join(contexts)
        return {"answer": answer, "sources": contexts, "retrieval_scores": [round(float(scores[i]), 4) for i in top_idx]}

    # ---------- Document intelligence ----------
    def _document_intelligence(self, text: str, features: dict, options: dict) -> dict:
        raw = text.strip() or "Record ID: DEMO-1001\nAmount: 1250\nOwner: Sample Team\nStatus: Open"
        patterns = {
            "record_id": r"(?:record\s*id|id)\s*[:#-]\s*([A-Za-z0-9_-]+)",
            "amount": r"(?:amount|total|value)\s*[:$-]\s*([0-9,.]+)",
            "owner": r"(?:owner|assigned\s*to)\s*[:#-]\s*([^\n]+)",
            "status": r"status\s*[:#-]\s*([^\n]+)",
        }
        extracted = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, raw, re.I)
            extracted[key] = match.group(1).strip() if match else None
        missing = [k for k, v in extracted.items() if not v]
        generated = self._ollama(f"Summarize this {settings.industry} document in 3 bullets:\n{raw}")
        summary = generated or "Document processed locally. Review extracted fields and missing-field flags before downstream action."
        return {"extracted_fields": extracted, "missing_fields": missing, "summary": summary, "requires_review": bool(missing)}

    # ---------- Forecasting ----------
    def _forecasting(self, text: str, features: dict, options: dict) -> dict:
        df = pd.read_csv(self.data_dir / "training.csv")
        model = LinearRegression().fit(df[["time"]], df["value"])
        horizon = int(options.get("horizon", 7))
        horizon = max(1, min(horizon, 90))
        last_t = int(df["time"].max())
        future = np.arange(last_t + 1, last_t + horizon + 1).reshape(-1, 1)
        preds = model.predict(future)
        return {
            "forecast": [{"time": int(t[0]), "value": round(float(v), 2)} for t, v in zip(future, preds)],
            "trend_per_period": round(float(model.coef_[0]), 4),
            "method": "linear_regression_baseline",
        }

    # ---------- Anomaly detection ----------
    def _anomaly_detection(self, text: str, features: dict, options: dict) -> dict:
        df = pd.read_csv(self.data_dir / "training.csv")
        feature_cols = [c for c in df.columns if c.startswith("x")]
        model = IsolationForest(contamination=0.08, random_state=42).fit(df[feature_cols])
        point = [float(features.get(c, df[c].median())) for c in feature_cols]
        pred = int(model.predict([point])[0])
        score = float(-model.decision_function([point])[0])
        return {"is_anomaly": pred == -1, "anomaly_score": round(score, 4), "input_features": dict(zip(feature_cols, point))}

    # ---------- Risk scoring ----------
    def _risk_scoring(self, text: str, features: dict, options: dict) -> dict:
        df = pd.read_csv(self.data_dir / "training.csv")
        cols = [c for c in df.columns if c.startswith("x")]
        model = LogisticRegression(max_iter=1000).fit(df[cols], df["label"])
        point = [float(features.get(c, df[c].median())) for c in cols]
        probability = float(model.predict_proba([point])[0, 1])
        band = "high" if probability >= .7 else "medium" if probability >= .4 else "low"
        return {"risk_probability": round(probability, 4), "risk_band": band, "recommended_action": "human_review" if band == "high" else "standard_processing"}

    # ---------- Recommendations ----------
    def _recommendation(self, text: str, features: dict, options: dict) -> dict:
        df = pd.read_csv(self.data_dir / "catalog.csv")
        query = text.strip() or "reliable fast low risk option"
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(df["description"].tolist() + [query])
        scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
        idx = scores.argsort()[::-1][:3]
        return {"recommendations": [
            {"item_id": str(df.iloc[i]["item_id"]), "name": df.iloc[i]["name"], "score": round(float(scores[i]), 4), "reason": df.iloc[i]["description"]}
            for i in idx
        ]}

    # ---------- Optimization ----------
    def _optimization(self, text: str, features: dict, options: dict) -> dict:
        df = pd.read_csv(self.data_dir / "training.csv")
        budget = float(features.get("budget", 100.0))
        # Greedy value/cost is intentionally transparent. Replace with MILP or a
        # domain solver when the business problem requires optimal guarantees.
        work = df.copy()
        work["ratio"] = work["value"] / work["cost"].clip(lower=.001)
        work = work.sort_values("ratio", ascending=False)
        selected, spent, value = [], 0.0, 0.0
        for row in work.itertuples():
            if spent + float(row.cost) <= budget:
                selected.append(str(row.item_id)); spent += float(row.cost); value += float(row.value)
        return {"selected_items": selected, "budget": budget, "spent": round(spent, 2), "estimated_value": round(value, 2), "method": "greedy_value_cost_baseline"}

    # ---------- Classification / triage ----------
    def _classification(self, text: str, features: dict, options: dict) -> dict:
        raw = (text or "routine request").lower()
        categories = {
            "urgent": ["urgent", "outage", "critical", "emergency", "blocked"],
            "financial": ["invoice", "payment", "charge", "cost", "refund"],
            "technical": ["error", "failed", "bug", "system", "device"],
            "general": [],
        }
        category = "general"
        for name, words in categories.items():
            if any(w in raw for w in words):
                category = name; break
        confidence = .9 if category != "general" else .62
        return {"category": category, "confidence": confidence, "route_to": f"{category}_queue", "requires_human_review": confidence < .75}

    # ---------- Support copilot ----------
    def _support_copilot(self, text: str, features: dict, options: dict) -> dict:
        issue = text.strip() or "User needs assistance with a routine request."
        llm = self._ollama(f"For {settings.industry}, summarize this issue and draft a concise support response:\n{issue}")
        if llm:
            draft = llm
        else:
            draft = f"Summary: {issue[:240]}\n\nRecommended response: Thank you for the details. We have captured the request and recommend validating the account/context, checking the relevant policy or system record, and escalating any exception that cannot be safely resolved automatically."
        return {"copilot_output": draft, "next_actions": ["validate_context", "check_relevant_record", "resolve_or_escalate"], "human_approval_required": True}

    # ---------- Agentic workflow ----------
    def _agentic_workflow(self, text: str, features: dict, options: dict) -> dict:
        goal = text.strip() or "Investigate the request and recommend the safest next action."
        # This demonstrates agent planning without allowing the demo to perform
        # irreversible external actions. Tool steps are simulated and auditable.
        plan = [
            {"step": 1, "tool": "retrieve_context", "status": "completed"},
            {"step": 2, "tool": "analyze_record", "status": "completed"},
            {"step": 3, "tool": "policy_check", "status": "completed"},
            {"step": 4, "tool": "propose_action", "status": "awaiting_human_approval"},
        ]
        generated = self._ollama(f"Create a concise action recommendation for this {settings.industry} goal: {goal}")
        return {"goal": goal, "plan": plan, "recommendation": generated or "Proceed with the lowest-risk validated action after human approval.", "execution_mode": "human_in_the_loop"}

    # ---------- KPI analytics ----------
    def _analytics(self, text: str, features: dict, options: dict) -> dict:
        df = pd.read_csv(self.data_dir / "training.csv")
        metric_cols = [c for c in df.columns if c.startswith("metric")]
        insights = []
        for col in metric_cols:
            series = df[col].astype(float)
            delta = float(series.iloc[-1] - series.iloc[0])
            pct = (delta / abs(float(series.iloc[0])) * 100) if series.iloc[0] != 0 else 0.0
            insights.append({"metric": col, "start": round(float(series.iloc[0]),2), "latest": round(float(series.iloc[-1]),2), "change_pct": round(pct,2)})
        driver = max(insights, key=lambda x: abs(x["change_pct"])) if insights else None
        return {"insights": insights, "largest_movement": driver, "root_cause_hypothesis": "Investigate the largest-moving KPI against recent operational, demand, and process changes."}

    # ---------- Compliance ----------
    def _compliance(self, text: str, features: dict, options: dict) -> dict:
        policy = (self.data_dir / "knowledge.txt").read_text(encoding="utf-8")
        candidate = text.strip() or "No approval recorded. Data will be retained indefinitely."
        checks = {
            "approval_present": bool(re.search(r"approved|approval", candidate, re.I)),
            "retention_defined": bool(re.search(r"retain|retention|days|years", candidate, re.I)),
            "review_present": bool(re.search(r"review|human", candidate, re.I)),
        }
        gaps = [k for k,v in checks.items() if not v]
        llm = self._ollama(f"Compare the candidate text to the policy. List only potential gaps.\nPOLICY:\n{policy}\nCANDIDATE:\n{candidate}")
        return {"checks": checks, "potential_gaps": gaps, "assessment": llm or ("Potential gaps found: " + ", ".join(gaps) if gaps else "No baseline gaps detected."), "disclaimer": "Demo control check; not legal or regulatory advice."}
