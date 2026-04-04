import pytest
from unittest.mock import patch, MagicMock

from app.products import service, models
from app.user.models import User
from app.categories.models import Category
from app.exceptions import ResourceDisableError, FileMaximumError


# === Helpers ===

def _make_user(db, username="testuser", email="test@example.com"):
    user = User(username=username, email=email, hashed_password="hashedpw")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_category(db, name="Elektronik"):
    cat = Category(name=name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def _make_product(db, user, category, name="Test Product", price=100.0, stock=10,
                  is_publish=True, image_url="/static/uploads/products/test.jpg"):
    product = models.Product(
        name=name,
        description="A test product",
        price=price,
        stock=stock,
        is_publish=is_publish,
        user_id=user.id,
        category_id=category.id,
        image_url=image_url,
        slug=f"{name.lower().replace(' ', '-')}-slug",
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def _fake_image(filename="photo.jpg", size=1024):
    img = MagicMock()
    img.filename = filename
    img.size = size
    img.file.read.return_value = b"\x00" * size
    return img


# ──────────────────────────────────────────────
#  delete_image
# ──────────────────────────────────────────────

class TestDeleteImage:
    @patch("app.products.service.os.remove")
    @patch("app.products.service.os.path.exists", return_value=True)
    def test_delete_existing_file(self, mock_exists, mock_remove):
        result = service.delete_image("/static/uploads/products/abc.jpg")

        mock_exists.assert_called_once_with("app/static/uploads/products/abc.jpg")
        mock_remove.assert_called_once_with("app/static/uploads/products/abc.jpg")
        assert result is True

    @patch("app.products.service.os.remove")
    @patch("app.products.service.os.path.exists", return_value=False)
    def test_delete_nonexistent_file(self, mock_exists, mock_remove):
        result = service.delete_image("/static/uploads/products/missing.jpg")

        mock_remove.assert_not_called()
        assert result is False

    def test_delete_empty_url(self):
        assert service.delete_image("") is False
        assert service.delete_image(None) is False


# ──────────────────────────────────────────────
#  save_image
# ──────────────────────────────────────────────

class TestSaveImage:
    def test_invalid_extension_raises(self):
        img = _fake_image(filename="document.pdf")

        with pytest.raises(ValueError, match="Invalid file type"):
            service.save_image(img)

    def test_exceeds_max_size_raises(self):
        img = _fake_image(size=6 * 1024 * 1024)

        with pytest.raises(FileMaximumError):
            service.save_image(img)

    @patch("builtins.open", new_callable=MagicMock)
    @patch("app.products.service.os.path.exists", return_value=True)
    def test_save_success_returns_url(self, mock_exists, mock_open):
        img = _fake_image(filename="photo.png", size=1024)

        url = service.save_image(img)

        assert url.startswith("/static/uploads/products/")
        assert url.endswith(".png")


# ──────────────────────────────────────────────
#  create_product
# ──────────────────────────────────────────────

class TestCreateProduct:
    def _product_data(self, user, category, **overrides):
        data = {
            "name": "Laptop Asus",
            "description": "Gaming laptop",
            "price": 15000.0,
            "stock": 5,
            "is_publish": True,
            "user_id": user.id,
            "category_id": category.id,
            "image": _fake_image(),
        }
        data.update(overrides)
        return data

    @patch("app.products.service.save_image", return_value="/static/uploads/products/fake.jpg")
    def test_create_success(self, mock_save, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)

        product = service.create_product(db_session, self._product_data(user, cat))

        assert product.id is not None
        assert product.name == "Laptop Asus"
        assert product.slug == f"laptop-asus-{product.id}"
        assert product.image_url == "/static/uploads/products/fake.jpg"

    def test_create_empty_name_raises(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)

        with pytest.raises(ValueError, match="Name cannot be empty"):
            service.create_product(db_session, self._product_data(user, cat, name="  "))

    def test_create_zero_price_raises(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)

        with pytest.raises(ValueError, match="Price cannot be lower than equal 0"):
            service.create_product(db_session, self._product_data(user, cat, price=0))

    def test_create_negative_price_raises(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)

        with pytest.raises(ValueError, match="Price cannot be lower than equal 0"):
            service.create_product(db_session, self._product_data(user, cat, price=-10))

    def test_create_negative_stock_raises(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)

        with pytest.raises(ValueError, match="Stock cannot be lower than 0"):
            service.create_product(db_session, self._product_data(user, cat, stock=-1))

    def test_create_invalid_category_raises(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)

        with pytest.raises(ValueError, match="Category is not found"):
            service.create_product(db_session, self._product_data(user, cat, category_id=9999))

    def test_create_no_image_raises(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)

        with pytest.raises(ValueError, match="Image is required"):
            service.create_product(db_session, self._product_data(user, cat, image=None))

    @patch("app.products.service.delete_image")
    @patch("app.products.service.save_image", return_value="/static/uploads/products/orphan.jpg")
    def test_create_db_error_cleans_up_image(self, mock_save, mock_delete, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)
        data = self._product_data(user, cat)

        with patch.object(db_session, "flush", side_effect=Exception("Simulated DB error")):
            with pytest.raises(RuntimeError, match="Database error"):
                service.create_product(db_session, data)

        mock_delete.assert_called_once_with("/static/uploads/products/orphan.jpg")


# ──────────────────────────────────────────────
#  get_products
# ──────────────────────────────────────────────

class TestGetProducts:
    def test_get_published_products(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)
        _make_product(db_session, user, cat, name="Published", is_publish=True)
        _make_product(db_session, user, cat, name="Draft", is_publish=False)

        products = service.get_products(db_session)

        assert len(products) == 1
        assert products[0].name == "Published"

    def test_get_products_by_username(self, db_session):
        user1 = _make_user(db_session, username="alice", email="alice@test.com")
        user2 = _make_user(db_session, username="bob", email="bob@test.com")
        cat = _make_category(db_session)
        _make_product(db_session, user1, cat, name="Alice Product")
        _make_product(db_session, user2, cat, name="Bob Product")

        products = service.get_products(db_session, username="alice")

        assert len(products) == 1
        assert products[0].name == "Alice Product"

    def test_get_products_empty(self, db_session):
        assert service.get_products(db_session) == []


# ──────────────────────────────────────────────
#  get_products_by_user_id
# ──────────────────────────────────────────────

class TestGetProductsByUserId:
    def test_returns_all_user_products(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)
        _make_product(db_session, user, cat, name="P1")
        _make_product(db_session, user, cat, name="P2")

        products = service.get_products_by_user_id(db_session, user.id)
        assert len(products) == 2

    def test_returns_empty_for_unknown_user(self, db_session):
        assert service.get_products_by_user_id(db_session, 9999) == []


# ──────────────────────────────────────────────
#  get_product_by_id
# ──────────────────────────────────────────────

class TestGetProductById:
    def test_get_published_product(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)
        p = _make_product(db_session, user, cat, is_publish=True)

        result = service.get_product_by_id(db_session, p.id)
        assert result.id == p.id

    def test_unpublished_raises(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)
        p = _make_product(db_session, user, cat, is_publish=False)

        with pytest.raises(ResourceDisableError):
            service.get_product_by_id(db_session, p.id)

    def test_not_found_returns_none(self, db_session):
        assert service.get_product_by_id(db_session, 9999) is None


# ──────────────────────────────────────────────
#  get_product_for_owner
# ──────────────────────────────────────────────

class TestGetProductForOwner:
    def test_owner_gets_product(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)
        p = _make_product(db_session, user, cat)

        result = service.get_product_for_owner(db_session, p.id, user.id)
        assert result.id == p.id

    def test_non_owner_gets_none(self, db_session):
        user1 = _make_user(db_session, username="owner", email="owner@test.com")
        user2 = _make_user(db_session, username="other", email="other@test.com")
        cat = _make_category(db_session)
        p = _make_product(db_session, user1, cat)

        assert service.get_product_for_owner(db_session, p.id, user2.id) is None

    def test_not_found_returns_none(self, db_session):
        assert service.get_product_for_owner(db_session, 9999, 1) is None


# ──────────────────────────────────────────────
#  update_product
# ──────────────────────────────────────────────

class TestUpdateProduct:
    def test_update_fields(self, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)
        p = _make_product(db_session, user, cat, name="Old", price=100)

        updated = service.update_product(db_session, p.id, {"name": "New", "price": 200})

        assert updated.name == "New"
        assert updated.price == 200

    @patch("app.products.service.delete_image")
    def test_update_with_new_image_deletes_old(self, mock_delete, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)
        p = _make_product(db_session, user, cat, image_url="/static/uploads/products/old.jpg")

        updated = service.update_product(db_session, p.id, {}, image_url="/static/uploads/products/new.jpg")

        mock_delete.assert_called_once_with("/static/uploads/products/old.jpg")
        assert updated.image_url == "/static/uploads/products/new.jpg"

    def test_update_not_found_returns_none(self, db_session):
        assert service.update_product(db_session, 9999, {"name": "X"}) is None


# ──────────────────────────────────────────────
#  delete_product
# ──────────────────────────────────────────────

class TestDeleteProduct:
    @patch("app.products.service.delete_image")
    def test_delete_success(self, mock_delete, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)
        p = _make_product(db_session, user, cat, image_url="/static/uploads/products/del.jpg")

        result = service.delete_product(db_session, p.id)

        assert result is True
        mock_delete.assert_called_once_with("/static/uploads/products/del.jpg")
        assert db_session.get(models.Product, p.id) is None

    def test_delete_not_found_returns_false(self, db_session):
        assert service.delete_product(db_session, 9999) is False

    @patch("app.products.service.delete_image")
    def test_delete_does_not_affect_others(self, mock_delete, db_session):
        user = _make_user(db_session)
        cat = _make_category(db_session)
        p1 = _make_product(db_session, user, cat, name="Keep")
        p2 = _make_product(db_session, user, cat, name="Remove")

        service.delete_product(db_session, p2.id)

        assert db_session.get(models.Product, p1.id) is not None
        assert db_session.query(models.Product).count() == 1
