# E-Commerce API (FastAPI)

A fully featured FastAPI backend that powers the marketplace experience for the React frontend. It handles registration/login, shop creation, product/catalog management, buyer-only purchasing, and Midtrans Snap payments.

## 🚀 Key Capabilities

- **Role-aware auth** – JWT scopes (`customer`, `shopowner`, `me`) are computed from database state so clients never supply scopes directly.
- **Shop lifecycle** – users can open a shop, upload a logo, and manage their inventory; non-owners stay in buyer mode.
- **Product catalog & categories** – CRUD with image uploads, publish toggle, stock tracking, owner linkage, plus reusable product categories.
- **Orders & payments** – order creation enforces “no self-purchase”, decrements stock, creates Midtrans transactions, and persists payment states/webhooks.
- **Static uploads & CORS** – product images/logos are served via FastAPI static files with configurable CORS origins for the frontend.

## ⚙️ Configuration

Create `backend/.env` (see `.env` committed for reference) and set:

| Variable | Description |
| --- | --- |
| `SECRET_KEY` / `ALGORITHM` / `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT configuration. |
| `MIDTRANS_SERVER_KEY` | Server key from Midtrans dashboard. |
| `MIDTRANS_CLIENT_KEY` | Client key returned to the frontend via `/payments/config`. |
| `MIDTRANS_IS_PRODUCTION` | `true` to hit production Snap API, otherwise sandbox. |
| `MIDTRANS_FINISH_REDIRECT_URL`, `MIDTRANS_ERROR_REDIRECT_URL`, `MIDTRANS_PENDING_REDIRECT_URL` | URLs Midtrans redirects to after checkout (point these to the frontend’s `/checkout/status`). |
| `MIDTRANS_USE_STUB` | `true` to bypass external calls during local development/tests. |
| `CORS_ORIGINS` | JSON list of allowed frontend origins (e.g. `["http://localhost:5173"]`). |

## 🛠️ Setup

```bash
cd backend
uv sync                 # install dependencies
uv run fastapi dev app/main.py
```

The API will be available at `http://127.0.0.1:8000` with documentation under `/docs` and `/redoc`.

### Running tests

```bash
uv run pytest
```

End-to-end order tests cover the new shop ownership rules and payment stubs.

## 🧩 Architecture snapshot

```
app/
├── user/        # auth, registration, scope helpers
├── shops/       # open/lookup shops and logo uploads
├── products/    # catalog CRUD + ownership enforcement
├── categories/  # product category model/service/router
├── orders/      # order placement, status transitions
├── payments/    # Midtrans integration & webhook
├── seeders/     # reusable data seed scripts
├── config.py    # settings model pulling from env
└── main.py      # FastAPI wiring, middleware, static files
```

Each domain follows the `models/schemas/service/router` pattern for clarity and testability.

### Seeding default categories

Populate the default category set (Pakaian, Elektronik, Rumah Tangga, etc.) by running:

```bash
uv run python -m app.seeders.categories
```

The script is idempotent and can be re-run safely; it only inserts categories that do not yet exist.
