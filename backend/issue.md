# Issue: Refactor Campaign — Rename FlashSale → Campaign, Buat API Endpoints, dan Integration Test

## Deskripsi

Empat perubahan besar pada modul **Campaign**:

1. Rename model `FlashSale` → `Campaign` dan `FlashSaleItems` → `CampaignItem` (termasuk nama tabel)
2. Rename semua method di service dari `flash_sale` → `campaign`, sesuaikan unit test
3. Buat API endpoints (router) untuk CRUD campaign
4. Buat integration test untuk semua endpoint yang dibuat

---

## Konteks Teknis

### File yang terlibat

| File | Peran |
|---|---|
| `app/campaign/models.py` | SQLAlchemy model `FlashSale` dan `FlashSaleItems` |
| `app/campaign/service.py` | Business logic campaign |
| `app/campaign/router.py` | HTTP endpoint campaign (saat ini kosong) |
| `app/campaign/schemas.py` | **Belum ada** — perlu dibuat untuk Pydantic schemas (request/response) |
| `app/main.py` | Registrasi router ke FastAPI app |
| `app/exceptions.py` | Custom exceptions (`NotFoundError`, `DuplicateEntryError`) |
| `tests/campaign/test_campaign_service.py` | Unit test service campaign |
| `tests/campaign/test_campaign_integration.py` | **Belum ada** — perlu dibuat untuk integration test |

### Model FlashSale saat ini (referensi)

```python
class FlashSale(TimeStampMixin, Base):
    __tablename__ = "flash_sales"

    id: Mapped[int]            # Primary key, autoincrement
    name: Mapped[str]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    is_active: Mapped[bool]    # default=True

    items → relationship ke FlashSaleItems


class FlashSaleItems(TimeStampMixin, Base):
    __tablename__ = "flash_sale_items"

    id: Mapped[int]            # Primary key, autoincrement
    flash_sale_id: Mapped[int] # FK ke flash_sales.id
    product_id: Mapped[int]    # FK ke products.id
    special_price: Mapped[float]
    stock_limit: Mapped[int]
    stock_sold: Mapped[int]    # default=0

    flash_sale → relationship ke FlashSale
    products → relationship ke Product
```

### Service methods saat ini

| Method lama | Penjelasan |
|---|---|
| `__validation_flash_sale(db, name, start_time, end_time, exclude_id)` | Validasi input (nama, tanggal, overlap) |
| `get_active_flash_sale(db)` | Ambil flash sale yang aktif saat ini |
| `create_flash_sale(db, name, end_time, start_time, is_active)` | Buat flash sale baru |
| `update_flash_sale(db, id, name, end_time, start_time, is_active)` | Update flash sale |
| `change_active_flash_sale(db, id)` | Toggle is_active |
| `delete_flash_sale(db, id)` | Hapus flash sale |

### Router saat ini (kosong)

```python
from fastapi import APIRouter
flash_sale_router = APIRouter("/flash-sale")
```

Router belum diregistrasikan di `app/main.py`.

### Custom Exceptions yang digunakan

- `NotFoundError(name="...")` → otomatis return HTTP 404 via global exception handler
- `DuplicateEntryError(name="...")` → otomatis return HTTP 409 via global exception handler
- `ValueError("...")` → harus di-catch manual di router dan return HTTP 400

### Dependency

- `TimeStampMixin` dari `app.database` memberikan field `created_at` dan `updated_at` otomatis
- `get_db` dari `app.database` untuk dependency injection database session
- `get_current_user` dari `app.user.dependencies` untuk autentikasi (scope: `"shopowner"`)
- `tests/conftest.py` menyediakan fixture `client` dan `db_session`

---

## Tahapan Implementasi

### Tahap 1: Rename Model FlashSale → Campaign

**Tujuan**: Rename model dan tabel database karena Flash Sale merupakan bagian dari Campaign.

**File**: `app/campaign/models.py`

**Langkah-langkah**:

1. Rename class `FlashSale` → `Campaign`
2. Ubah `__tablename__` dari `"flash_sales"` → `"campaigns"`
3. Rename relationship `items` → tetap `items`, tapi back_populates harus disesuaikan
4. Rename class `FlashSaleItems` → `CampaignItem`
5. Ubah `__tablename__` dari `"flash_sale_items"` → `"campaign_items"`
6. Rename field `flash_sale_id` → `campaign_id`
7. Ubah ForeignKey dari `'flash_sales.id'` → `'campaigns.id'`
8. Rename relationship `flash_sale` → `campaign`, ubah `back_populates='items'`
9. Sesuaikan relationship di `Campaign`: `back_populates='flash_sale'` → `back_populates='campaign'`

**Hasil akhir yang diharapkan**:

```python
from datetime import datetime
from app.database import Base, TimeStampMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column


class Campaign(TimeStampMixin, Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    items = relationship('CampaignItem', back_populates='campaign')


class CampaignItem(TimeStampMixin, Base):
    __tablename__ = "campaign_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    special_price: Mapped[float] = mapped_column(nullable=False)
    stock_limit: Mapped[int] = mapped_column(nullable=False)
    stock_sold: Mapped[int] = mapped_column(default=0)

    campaign = relationship('Campaign', back_populates='items')
    products = relationship('Product')
```

---

### Tahap 2: Rename Service Methods flash_sale → campaign

**Tujuan**: Semua method di service menggunakan penamaan `campaign` agar konsisten dengan model baru.

**File**: `app/campaign/service.py`

**Mapping rename method**:

| Method lama | Method baru |
|---|---|
| `__validation_flash_sale()` | `__validation_campaign()` |
| `get_active_flash_sale()` | `get_active_campaign()` |
| `create_flash_sale()` | `create_campaign()` |
| `update_flash_sale()` | `update_campaign()` |
| `change_active_flash_sale()` | `change_active_campaign()` |
| `delete_flash_sale()` | `delete_campaign()` |

**Langkah-langkah**:

1. Rename semua function sesuai tabel di atas
2. Ganti semua referensi `models.FlashSale` → `models.Campaign` di dalam service
3. Ganti semua string error message yang mengandung `"flash sale"` → `"campaign"`. Contoh:
   - `"Failed to check overlapping flash sales"` → `"Failed to check overlapping campaigns"`
   - `"Flash sale '{name}' overlaps with existing flash sale"` → `"Campaign '{name}' overlaps with existing campaign"`
   - `"No active flash sale found"` → `"No active campaign found"`
   - `"Failed to fetch active flash sale"` → `"Failed to fetch active campaign"`
   - `"Failed to create flash sale"` → `"Failed to create campaign"`
   - `"Failed to update flash sale"` → `"Failed to update campaign"`
   - `"Failed to change active flash sale"` → `"Failed to change active campaign"`
4. Service method `create_campaign` dan `update_campaign` harus **mengembalikan object campaign** (saat ini return `None`). Tambahkan `db.refresh(...)` dan `return ...` setelah commit agar router bisa mengembalikan data campaign ke response.

**Penting — ubah return value**:

Saat ini `create_flash_sale()` dan `update_flash_sale()` return `None`. Ubah agar return object campaign:

```python
def create_campaign(db, name, end_time, start_time, is_active) -> models.Campaign:
    # ... (validasi & buat campaign)
    db.add(campaign)
    db.commit()
    db.refresh(campaign)  # ← tambahkan
    return campaign        # ← tambahkan

def update_campaign(db, id, name, end_time, start_time, is_active) -> models.Campaign:
    # ... (validasi & update fields)
    db.commit()
    db.refresh(updated_campaign)  # ← tambahkan
    return updated_campaign         # ← tambahkan

def change_active_campaign(db, id) -> models.Campaign:
    # ... (toggle is_active)
    db.commit()
    db.refresh(updated_campaign)  # ← tambahkan
    return updated_campaign         # ← tambahkan
```

---

### Tahap 3: Sesuaikan Unit Test Service

**Tujuan**: Ubah test agar menggunakan nama method dan model baru.

**File**: `tests/campaign/test_campaign_service.py`

**Langkah-langkah**:

1. **Ubah helper `_make_flash_sale()`** → rename menjadi `_make_campaign()`:
   - Ganti `models.FlashSale(...)` → `models.Campaign(...)`
   - Ubah nama parameter dan variable di dalamnya

2. **Rename semua class test**:

   | Class lama | Class baru |
   |---|---|
   | `TestCreateFlashSale` | `TestCreateCampaign` |
   | `TestGetActiveFlashSale` | `TestGetActiveCampaign` |
   | `TestUpdateFlashSale` | `TestUpdateCampaign` |
   | `TestChangeActiveFlashSale` | `TestChangeActiveCampaign` |
   | `TestDeleteFlashSale` | `TestDeleteCampaign` |

3. **Di setiap test method**, ubah:
   - `service.create_flash_sale(...)` → `service.create_campaign(...)`
   - `service.get_active_flash_sale(...)` → `service.get_active_campaign(...)`
   - `service.update_flash_sale(...)` → `service.update_campaign(...)`
   - `service.change_active_flash_sale(...)` → `service.change_active_campaign(...)`
   - `service.delete_flash_sale(...)` → `service.delete_campaign(...)`
   - `db_session.query(models.FlashSale)` → `db_session.query(models.Campaign)`
   - `db_session.get(models.FlashSale, ...)` → `db_session.get(models.Campaign, ...)`

4. **Ubah string match di pytest.raises**:
   - `"overlaps with existing flash sale"` → `"overlaps with existing campaign"`

5. **Jalankan test** untuk memastikan semua pass:
   ```bash
   cd backend
   python -m pytest tests/campaign/test_campaign_service.py -v
   ```

---

### Tahap 4: Buat Pydantic Schemas

**Tujuan**: Buat file schemas untuk request/response validation.

**File**: `app/campaign/schemas.py` (file baru)

**Buat schemas berikut**:

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CampaignCreate(BaseModel):
    name: str
    start_time: Optional[datetime] = None  # default: hari ini (diisi di service)
    end_time: datetime
    is_active: bool = True


class CampaignUpdate(BaseModel):
    name: str
    start_time: Optional[datetime] = None  # default: hari ini (diisi di service)
    end_time: datetime
    is_active: bool = True


class CampaignResponse(BaseModel):
    id: int
    name: str
    start_time: datetime
    end_time: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

---

### Tahap 5: Buat API Endpoints (Router)

**Tujuan**: Buat endpoint-endpoint REST API untuk campaign.

**File**: `app/campaign/router.py` (replace isi yang ada)

#### 5a. Setup Router

```python
from typing import Annotated, List
from fastapi import APIRouter, Depends, Security, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.user.dependencies import get_current_user
from app.user.models import User
from . import schemas, service

router = APIRouter(prefix="/campaign", tags=["Campaign"])
```

**Penting**:
- Ganti variable dari `flash_sale_router` → `router` agar konsisten dengan modul lain
- Prefix: `/campaign`
- Semua endpoint memerlukan autentikasi dengan scope `"shopowner"`, kecuali GET active campaign

#### 5b. Endpoint: POST /campaign/

**Fungsi**: Membuat campaign baru.

**Logika**:
1. Panggil `service.create_campaign(db, ...)` dengan data dari request body
2. Jika `start_time` tidak diberikan, service akan menggunakan waktu saat ini sebagai default
3. Catch `ValueError` → return HTTP 400 dengan `{"message": str(error)}`
4. Jika sukses → return HTTP 201 dengan body:

```json
{
    "message": "Campaign created successfully",
    "data": {
        "id": 1,
        "name": "Year End Sale",
        "start_time": "2026-04-06T00:00:00",
        "end_time": "2026-04-10T00:00:00",
        "is_active": true,
        "created_at": "2026-04-06T04:47:07",
        "updated_at": "2026-04-06T04:47:07"
    }
}
```

**Contoh implementasi**:

```python
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_campaign(
    payload: schemas.CampaignCreate,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        campaign = service.create_campaign(
            db,
            name=payload.name,
            start_time=payload.start_time,
            end_time=payload.end_time,
            is_active=payload.is_active,
        )
        return {
            "message": "Campaign created successfully",
            "data": schemas.CampaignResponse.model_validate(campaign).model_dump(),
        }
    except ValueError as err:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(err)},
        )
```

#### 5c. Endpoint: GET /campaign/active

**Fungsi**: Mendapatkan daftar campaign yang sedang aktif (berdasarkan waktu saat ini, yaitu `start_time <= now <= end_time`).

**Catatan penting**: Saat ini `get_active_campaign()` di service hanya mengembalikan **satu** campaign (`.first()`). Perlu **diubah** agar mengembalikan **semua** campaign aktif (`.all()`), karena response body membutuhkan array `Campaign[]`.

**Ubah service `get_active_campaign()`**:

```python
def get_active_campaign(db: Session):
    now = datetime.now()
    try:
        campaigns = (db.query(models.Campaign)
                      .filter(models.Campaign.start_time <= now)
                      .filter(models.Campaign.end_time >= now)
                      .all())  # ← ubah dari .first() ke .all()
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to fetch active campaign: {err}")

    return campaigns  # ← return list, jangan raise NotFoundError jika kosong
```

**Response body** (Success):

```json
{
    "data": [
        {
            "id": 1,
            "name": "Year End Sale",
            "start_time": "2026-04-06T00:00:00",
            "end_time": "2026-04-10T00:00:00",
            "is_active": true,
            "created_at": "...",
            "updated_at": "..."
        }
    ]
}
```

**Contoh implementasi**:

```python
@router.get("/active")
def get_active_campaigns(db: Session = Depends(get_db)):
    try:
        campaigns = service.get_active_campaign(db)
        return {
            "data": [
                schemas.CampaignResponse.model_validate(c).model_dump()
                for c in campaigns
            ],
        }
    except RuntimeError as err:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(err)},
        )
```

**Endpoint ini tidak memerlukan autentikasi** — campaign aktif bisa dilihat oleh siapa saja (publik).

#### 5d. Endpoint: PUT /campaign/{campaign_id}

**Fungsi**: Mengubah data campaign.

**Logika**:
1. Panggil `service.update_campaign(db, id=campaign_id, ...)` dengan data dari request body
2. Catch `ValueError` → return HTTP 400 dengan `{"message": str(error)}`
3. `NotFoundError` akan otomatis di-handle oleh global exception handler (HTTP 404)
4. Jika sukses → return HTTP 200 dengan body:

```json
{
    "message": "Campaign updated successfully",
    "data": {
        "id": 1,
        "name": "Updated Name",
        "start_time": "2026-04-06T00:00:00",
        "end_time": "2026-04-15T00:00:00",
        "is_active": true,
        "created_at": "...",
        "updated_at": "..."
    }
}
```

**Contoh implementasi**:

```python
@router.put("/{campaign_id}")
def update_campaign(
    campaign_id: int,
    payload: schemas.CampaignUpdate,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        campaign = service.update_campaign(
            db,
            id=campaign_id,
            name=payload.name,
            start_time=payload.start_time,
            end_time=payload.end_time,
            is_active=payload.is_active,
        )
        return {
            "message": "Campaign updated successfully",
            "data": schemas.CampaignResponse.model_validate(campaign).model_dump(),
        }
    except ValueError as err:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(err)},
        )
```

#### 5e. Endpoint: PATCH /campaign/{campaign_id}/active

**Fungsi**: Toggle aktif/nonaktif campaign.

**Logika**:
1. Panggil `service.change_active_campaign(db, id=campaign_id)`
2. `NotFoundError` akan otomatis di-handle oleh global exception handler (HTTP 404)
3. Jika sukses → return HTTP 200 dengan body:

```json
{
    "message": "Campaign activated successfully",
    "data": {
        "id": 1,
        "name": "Year End Sale",
        "start_time": "...",
        "end_time": "...",
        "is_active": true,
        "created_at": "...",
        "updated_at": "..."
    }
}
```

**Catatan**: Message disesuaikan berdasarkan status baru:
- Jika `is_active` menjadi `True` → `"Campaign activated successfully"`
- Jika `is_active` menjadi `False` → `"Campaign deactivated successfully"`

**Contoh implementasi**:

```python
@router.patch("/{campaign_id}/active")
def toggle_campaign_active(
    campaign_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    campaign = service.change_active_campaign(db, id=campaign_id)
    action = "activated" if campaign.is_active else "deactivated"
    return {
        "message": f"Campaign {action} successfully",
        "data": schemas.CampaignResponse.model_validate(campaign).model_dump(),
    }
```

---

### Tahap 6: Registrasi Router di main.py

**File**: `app/main.py`

**Langkah-langkah**:

1. Tambahkan import router campaign:

```python
from app.campaign.router import router as campaign_router
```

2. Tambahkan `app.include_router(campaign_router)` di bawah router yang sudah ada:

```python
# Include Routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(shop_router)
app.include_router(payment_router)
app.include_router(category_router)
app.include_router(campaign_router)    # ← tambahkan
```

---

### Tahap 7: Buat Integration Test

**Tujuan**: Test semua endpoint campaign melalui HTTP client.

**File**: `tests/campaign/test_campaign_integration.py` (file baru)

#### 7a. Setup Helpers

Gunakan pola yang sama dengan test module lain:

```python
import pytest
from datetime import datetime, timedelta


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _setup_shopowner(client, username="seller", email="seller@test.com"):
    """Register → login → create shop → re-login untuk dapat scope shopowner."""
    client.post("/register", json={
        "username": username, "email": email,
        "password": "password123", "disable": False,
    })
    login = client.post("/token", data={"username": username, "password": "password123"})
    token = login.json()["access_token"]

    client.post("/shops/", headers=_auth(token), data={
        "name": f"{username} Shop", "description": "Test shop",
    })

    login = client.post("/token", data={"username": username, "password": "password123"})
    return login.json()["access_token"]


def _today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
```

#### 7b. Test Classes

| Class | Test yang dicakup |
|---|---|
| `TestCreateCampaign` | Create campaign sukses (201), validasi nama kosong (400), validasi start_time di masa lalu (400), validasi end_time <= start_time (400), overlapping campaign (400) |
| `TestGetActiveCampaign` | Get active campaign sukses (200, return array), tidak ada campaign aktif (200, return array kosong) |
| `TestUpdateCampaign` | Update campaign sukses (200), campaign tidak ditemukan (404), validasi input error (400) |
| `TestToggleCampaignActive` | Toggle active → inactive (200), toggle inactive → active (200), campaign tidak ditemukan (404) |
| `TestCampaignAuthorization` | Create tanpa token → 401, update tanpa token → 401, toggle tanpa token → 401, GET active tanpa token → 200 (publik) |

#### 7c. Contoh test untuk setiap endpoint

```python
class TestCreateCampaign:
    def test_create_success(self, client):
        token = _setup_shopowner(client)

        start = _today().isoformat()
        end = (_today() + timedelta(days=3)).isoformat()

        resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Year End Sale",
            "start_time": start,
            "end_time": end,
        })

        assert resp.status_code == 201
        body = resp.json()
        assert body["message"] == "Campaign created successfully"
        assert body["data"]["name"] == "Year End Sale"
        assert body["data"]["is_active"] is True
        assert body["data"]["id"] is not None

    def test_create_empty_name(self, client):
        token = _setup_shopowner(client)

        resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "   ",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })

        assert resp.status_code == 400
        assert "message" in resp.json()

    def test_create_start_time_in_past(self, client):
        token = _setup_shopowner(client)

        resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Sale",
            "start_time": (_today() - timedelta(days=1)).isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })

        assert resp.status_code == 400

    def test_create_end_time_before_start(self, client):
        token = _setup_shopowner(client)

        resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Sale",
            "start_time": (_today() + timedelta(days=5)).isoformat(),
            "end_time": _today().isoformat(),
        })

        assert resp.status_code == 400

    def test_create_overlapping(self, client):
        token = _setup_shopowner(client)

        start = _today().isoformat()
        end = (_today() + timedelta(days=5)).isoformat()

        # Create first campaign
        resp1 = client.post("/campaign/", headers=_auth(token), json={
            "name": "First Sale",
            "start_time": start,
            "end_time": end,
        })
        assert resp1.status_code == 201

        # Try overlapping campaign
        resp2 = client.post("/campaign/", headers=_auth(token), json={
            "name": "Second Sale",
            "start_time": (_today() + timedelta(days=1)).isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })
        assert resp2.status_code == 400


class TestGetActiveCampaign:
    def test_get_active_success(self, client):
        token = _setup_shopowner(client)

        # Create campaign yang mencakup hari ini
        start = (_today() - timedelta(days=1)).isoformat()
        end = (_today() + timedelta(days=3)).isoformat()

        # Buat campaign langsung via POST (start_time in past akan error via validasi)
        # Sebagai alternatif, buat campaign dengan start_time = hari ini
        client.post("/campaign/", headers=_auth(token), json={
            "name": "Active Sale",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })

        resp = client.get("/campaign/active")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert isinstance(body["data"], list)

    def test_get_active_empty(self, client):
        # Tidak ada campaign aktif
        resp = client.get("/campaign/active")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"] == []


class TestUpdateCampaign:
    def test_update_success(self, client):
        token = _setup_shopowner(client)

        # Create campaign
        create_resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Old Name",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })
        campaign_id = create_resp.json()["data"]["id"]

        # Update campaign
        new_end = (_today() + timedelta(days=5)).isoformat()
        resp = client.put(f"/campaign/{campaign_id}", headers=_auth(token), json={
            "name": "New Name",
            "start_time": _today().isoformat(),
            "end_time": new_end,
        })

        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "Campaign updated successfully"
        assert body["data"]["name"] == "New Name"

    def test_update_not_found(self, client):
        token = _setup_shopowner(client)

        resp = client.put("/campaign/9999", headers=_auth(token), json={
            "name": "Name",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })

        assert resp.status_code == 404

    def test_update_empty_name(self, client):
        token = _setup_shopowner(client)

        create_resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Campaign",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })
        campaign_id = create_resp.json()["data"]["id"]

        resp = client.put(f"/campaign/{campaign_id}", headers=_auth(token), json={
            "name": "  ",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })

        assert resp.status_code == 400


class TestToggleCampaignActive:
    def test_toggle_active_to_inactive(self, client):
        token = _setup_shopowner(client)

        create_resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Campaign",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
            "is_active": True,
        })
        campaign_id = create_resp.json()["data"]["id"]

        resp = client.patch(f"/campaign/{campaign_id}/active", headers=_auth(token))

        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "Campaign deactivated successfully"
        assert body["data"]["is_active"] is False

    def test_toggle_inactive_to_active(self, client):
        token = _setup_shopowner(client)

        create_resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Campaign",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
            "is_active": False,
        })
        campaign_id = create_resp.json()["data"]["id"]

        # Karena is_active awal = False, toggle → True
        # Tapi perlu dicek: apakah create_campaign menerima is_active=False?
        # Jika service default is_active=True, maka toggle pertama → False
        # Sesuaikan test berdasarkan perilaku aktual

        resp = client.patch(f"/campaign/{campaign_id}/active", headers=_auth(token))
        assert resp.status_code == 200

    def test_toggle_not_found(self, client):
        token = _setup_shopowner(client)

        resp = client.patch("/campaign/9999/active", headers=_auth(token))
        assert resp.status_code == 404


class TestCampaignAuthorization:
    def test_create_without_token(self, client):
        resp = client.post("/campaign/", json={
            "name": "Sale",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })
        assert resp.status_code == 401

    def test_update_without_token(self, client):
        resp = client.put("/campaign/1", json={
            "name": "Sale",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })
        assert resp.status_code == 401

    def test_toggle_without_token(self, client):
        resp = client.patch("/campaign/1/active")
        assert resp.status_code == 401

    def test_get_active_without_token(self, client):
        # GET active campaign harus bisa diakses tanpa login (publik)
        resp = client.get("/campaign/active")
        assert resp.status_code == 200
```

#### 7d. Jalankan test dan perbaiki

```bash
cd backend
python -m pytest tests/campaign/ -v
```

Jika ada test yang gagal, analisis penyebabnya lalu perbaiki kode (bukan testnya) kecuali memang testnya yang salah.

---

## Format Response Error

Semua error response menggunakan format `{"message": "..."}`:

```python
# Untuk ValueError di router, gunakan JSONResponse:
from fastapi.responses import JSONResponse
return JSONResponse(
    status_code=status.HTTP_400_BAD_REQUEST,
    content={"message": str(err)},
)
```

**Catatan**: `NotFoundError` dan `DuplicateEntryError` di-handle oleh global exception handler yang sudah ada di `app/exceptions.py`. Response format dari global handler menggunakan `{"detail": "..."}` — ini **berbeda** dari format `{"message": "..."}` yang diminta. Jika ingin **konsisten** menggunakan `{"message": "..."}` untuk semua error termasuk 404, maka catch `NotFoundError` secara manual di router daripada membiarkan global handler menanganinya:

```python
# Opsi 1 — Biarkan global handler (response: {"detail": "Not found: ..."})
# Tidak perlu catch NotFoundError di router

# Opsi 2 — Catch manual untuk konsisten pakai "message" (DIREKOMENDASIKAN)
try:
    campaign = service.update_campaign(db, ...)
    return { ... }
except ValueError as err:
    return JSONResponse(status_code=400, content={"message": str(err)})
except NotFoundError as err:
    return JSONResponse(status_code=404, content={"message": str(err.name)})
```

---

## Checklist

- [ ] Rename model `FlashSale` → `Campaign` di `models.py`
- [ ] Rename model `FlashSaleItems` → `CampaignItem` di `models.py`
- [ ] Ubah `__tablename__` menjadi `"campaigns"` dan `"campaign_items"`
- [ ] Rename FK `flash_sale_id` → `campaign_id`
- [ ] Rename semua method service dari `flash_sale` → `campaign`
- [ ] Ganti semua referensi `models.FlashSale` → `models.Campaign` di service
- [ ] Ubah error message string dari "flash sale" → "campaign"
- [ ] Ubah `create_campaign()` dan `update_campaign()` agar return object campaign
- [ ] Ubah `change_active_campaign()` agar return object campaign
- [ ] Ubah `get_active_campaign()` agar return list (`.all()`) bukan single (`.first()`)
- [ ] Sesuaikan unit test di `test_campaign_service.py`
- [ ] Buat file `app/campaign/schemas.py` (CampaignCreate, CampaignUpdate, CampaignResponse)
- [ ] Buat router di `app/campaign/router.py` dengan 4 endpoint
- [ ] Registrasi campaign router di `app/main.py`
- [ ] Buat integration test di `tests/campaign/test_campaign_integration.py`
- [ ] Jalankan `pytest tests/campaign/ -v` → semua test harus pass
