# E-Commerce Monorepo

Monorepo e-commerce dengan backend FastAPI dan frontend React + Vite.

## Teknologi

- Python 3.13
- FastAPI
- SQLAlchemy
- Pytest
- React 19
- TypeScript
- Vite
- Material UI
- Zustand
- React Router
- Midtrans Snap

## Struktur

- `app/` backend FastAPI
- `resources/` source frontend
- `resources/public/` aset statis frontend
- `dist/` hasil build frontend
- `test/backend/` test backend
- `main.py` entrypoint backend
- `.env` konfigurasi lokal

## Konfigurasi

Gunakan `.env` di root untuk mengatur:

- `PORT` untuk backend
- `VITE_PORT` untuk frontend dev server
- `VITE_API_URL` untuk base URL API frontend
- `MIDTRANS_*` untuk konfigurasi pembayaran
- `CORS_ORIGINS` untuk origin yang diizinkan backend

## Menjalankan project

```bash
make install
make dev
```

Perintah lain:

```bash
make test
make build
```

## Catatan

- Backend berjalan lewat `main.py` dan prefix API memakai `/api`.
- Frontend dev server memakai port dari `VITE_PORT` dan proxy `/api` ke backend.
