import pytest

from app.categories import service, schemas, models
from app.categories.models import Category
from app.products.models import Product
from app.user.models import User
from app.exceptions import NotFoundError, DuplicateEntryError


# === Helpers ===

def _make_category(db, name="Elektronik", description=None, icon=None):
    cat = Category(name=name, description=description, icon=icon)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def _make_user(db, username="testuser", email="test@example.com"):
    user = User(username=username, email=email, hashed_password="hashedpw")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_product(db, user, category, name="Product"):
    product = Product(
        name=name, description="desc", price=100, stock=10,
        is_publish=True, user_id=user.id, category_id=category.id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# ──────────────────────────────────────────────
#  create_category
# ──────────────────────────────────────────────

class TestCreateCategory:
    def test_create_success(self, db_session):
        payload = schemas.CategoryCreate(name="Pakaian", description="Semua busana")
        cat = service.create_category(db_session, payload)

        assert cat.id is not None
        assert cat.name == "Pakaian"
        assert cat.description == "Semua busana"

    def test_create_with_icon(self, db_session):
        payload = schemas.CategoryCreate(name="Makanan", icon="food-icon.png")
        cat = service.create_category(db_session, payload)

        assert cat.icon == "food-icon.png"

    def test_create_empty_name_raises(self, db_session):
        payload = schemas.CategoryCreate(name="  ")

        with pytest.raises(ValueError, match="Name cannot be empty"):
            service.create_category(db_session, payload)

    def test_create_duplicate_name_raises(self, db_session):
        _make_category(db_session, name="Elektronik")
        payload = schemas.CategoryCreate(name="Elektronik")

        with pytest.raises(DuplicateEntryError):
            service.create_category(db_session, payload)


# ──────────────────────────────────────────────
#  get_category
# ──────────────────────────────────────────────

class TestGetCategory:
    def test_get_existing(self, db_session):
        cat = _make_category(db_session, name="Olahraga")

        result = service.get_category(db_session, cat.id)
        assert result is not None
        assert result.name == "Olahraga"

    def test_get_not_found_returns_none(self, db_session):
        assert service.get_category(db_session, 9999) is None


# ──────────────────────────────────────────────
#  list_categories
# ──────────────────────────────────────────────

class TestListCategories:
    def test_list_returns_all(self, db_session):
        _make_category(db_session, name="B-Pakaian")
        _make_category(db_session, name="A-Elektronik")

        result = service.list_categories(db_session)
        assert len(result) == 2

    def test_list_sorted_by_name(self, db_session):
        _make_category(db_session, name="Zebra")
        _make_category(db_session, name="Alpha")

        result = service.list_categories(db_session)
        assert result[0].name == "Alpha"
        assert result[1].name == "Zebra"

    def test_list_empty(self, db_session):
        assert service.list_categories(db_session) == []


# ──────────────────────────────────────────────
#  update_category
# ──────────────────────────────────────────────

class TestUpdateCategory:
    def test_update_description(self, db_session):
        cat = _make_category(db_session, name="Pakaian", description="Old")

        updated = service.update_category(
            db_session, cat.id,
            schemas.CategoryUpdate(description="Busana lengkap"),
        )

        assert updated.description == "Busana lengkap"
        assert updated.name == "Pakaian"

    def test_update_name(self, db_session):
        cat = _make_category(db_session, name="Old Name")

        updated = service.update_category(
            db_session, cat.id,
            schemas.CategoryUpdate(name="New Name"),
        )

        assert updated.name == "New Name"

    def test_update_not_found_raises(self, db_session):
        with pytest.raises(NotFoundError):
            service.update_category(
                db_session, 9999,
                schemas.CategoryUpdate(name="X"),
            )

    def test_update_empty_name_raises(self, db_session):
        cat = _make_category(db_session, name="Valid")

        with pytest.raises(ValueError, match="Name cannot be empty"):
            service.update_category(
                db_session, cat.id,
                schemas.CategoryUpdate(name="  "),
            )

    def test_update_duplicate_name_raises(self, db_session):
        _make_category(db_session, name="Existing")
        cat = _make_category(db_session, name="ToUpdate")

        with pytest.raises(DuplicateEntryError):
            service.update_category(
                db_session, cat.id,
                schemas.CategoryUpdate(name="Existing"),
            )

    def test_partial_update_keeps_other_fields(self, db_session):
        cat = _make_category(db_session, name="Cat", description="Desc", icon="icon.png")

        updated = service.update_category(
            db_session, cat.id,
            schemas.CategoryUpdate(icon="new-icon.png"),
        )

        assert updated.name == "Cat"
        assert updated.description == "Desc"
        assert updated.icon == "new-icon.png"


# ──────────────────────────────────────────────
#  delete_category
# ──────────────────────────────────────────────

class TestDeleteCategory:
    def test_delete_success(self, db_session):
        cat = _make_category(db_session, name="ToDelete")

        service.delete_category(db_session, cat.id)

        assert service.get_category(db_session, cat.id) is None

    def test_delete_not_found_raises(self, db_session):
        with pytest.raises(NotFoundError):
            service.delete_category(db_session, 9999)

    def test_delete_does_not_affect_others(self, db_session):
        cat1 = _make_category(db_session, name="Keep")
        cat2 = _make_category(db_session, name="Remove")

        service.delete_category(db_session, cat2.id)

        assert service.get_category(db_session, cat1.id) is not None
        assert db_session.query(models.Category).count() == 1

    def test_delete_unlinks_products(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session, name="ToBeDel")
        product = _make_product(db_session, user, cat)

        service.delete_category(db_session, cat.id)

        db_session.refresh(product)
        assert product.category_id is None
