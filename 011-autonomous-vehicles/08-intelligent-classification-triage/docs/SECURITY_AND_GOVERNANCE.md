# Security, Governance, and Production Checklist

- Do not place secrets in source code; use environment variables or a secrets manager.
- Add authentication and authorization before exposing the API to real users.
- Validate all external inputs and apply payload size limits.
- Redact or tokenize sensitive data before model processing when required.
- Log model/version metadata and important decisions for auditability.
- Define confidence thresholds and human-review rules before automating actions.
- Add rate limits, timeouts, retries, and circuit breakers around external services.
- Monitor latency, errors, data drift, model quality, cost, and business KPIs.
- Use domain experts to validate safety, regulatory, clinical, financial, legal, or other high-impact decisions.
- Replace demo sample data with approved data pipelines and documented lineage before production use.
