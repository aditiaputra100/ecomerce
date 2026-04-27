---
description: "Use when creating or modifying FastAPI endpoints, routers, or backend API flows. Prefer router-to-service layering and add unit plus integration tests for every new endpoint method."
name: "Backend Endpoint Quality"
applyTo: ["app/**/*.py", "test/backend/**/*.py"]
---
# Backend Endpoint Quality

These are best-effort preferences for backend changes.

- Keep routers thin: parse request data and delegate business logic to the service layer.
- Put business rules in service modules so they are testable without HTTP wiring.
- For every newly created endpoint method (GET, POST, PUT, DELETE, PATCH), add unit tests for service behavior, edge cases, and failures.
- For every newly created endpoint method (GET, POST, PUT, DELETE, PATCH), add integration tests that exercise request-to-response behavior, including status codes and payload shape.
- If a test is intentionally deferred, leave a short note in the PR or code comments with the reason and planned follow-up.
