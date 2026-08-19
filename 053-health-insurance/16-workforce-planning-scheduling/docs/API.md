# API

## `GET /health`
Returns service health and project identity.

## `GET /metadata`
Returns the configured industry, use case, and task type.

## `POST /predict`

Example request:

```json
{
  "text": "Describe the business record, question, or issue here.",
  "features": {"x1": 1.2, "x2": 3.4, "x3": 5.6, "budget": 100},
  "options": {"horizon": 7}
}
```

The shape of `result` depends on the project's task type.

## `GET /history?limit=20`
Returns recent inputs and outputs persisted to SQLite.
