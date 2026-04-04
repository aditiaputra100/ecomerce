import pytest
from datetime import datetime, timedelta, timezone

from app.campaign import service, models
from app.exceptions import NotFoundError


# === Helper ===

def _today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def _make_flash_sale(db, name="Flash Sale", days_offset=0, duration_days=2, is_active=True):
    """Insert a FlashSale directly into the DB and return it."""
    start = _today() + timedelta(days=days_offset)
    end = start + timedelta(days=duration_days)
    fs = models.FlashSale(
        name=name,
        start_time=start,
        end_time=end,
        is_active=is_active,
    )
    db.add(fs)
    db.commit()
    db.refresh(fs)
    return fs


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
#  create_flash_sale
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class TestCreateFlashSale:
    def test_create_success(self, db_session):
        start = _today()
        end = start + timedelta(days=3)

        service.create_flash_sale(
            db_session,
            name="Year End Sale",
            start_time=start,
            end_time=end,
        )

        result = db_session.query(models.FlashSale).first()
        assert result is not None
        assert result.name == "Year End Sale"
        assert result.is_active is True

    def test_create_empty_name_raises(self, db_session):
        start = _today()
        end = start + timedelta(days=3)

        with pytest.raises(ValueError, match="Name cannot be empty"):
            service.create_flash_sale(db_session, name="  ", start_time=start, end_time=end)

    def test_create_start_time_in_past_raises(self, db_session):
        start = _today() - timedelta(days=1)
        end = start + timedelta(days=3)

        with pytest.raises(ValueError, match="Start time cannot be earlier than today"):
            service.create_flash_sale(db_session, name="Sale", start_time=start, end_time=end)

    def test_create_end_time_equal_start_raises(self, db_session):
        start = _today()
        end = start  # same date

        with pytest.raises(ValueError, match="End time cannot be earlier or equal than start time"):
            service.create_flash_sale(db_session, name="Sale", start_time=start, end_time=end)

    def test_create_end_time_before_start_raises(self, db_session):
        start = _today() + timedelta(days=5)
        end = _today()

        with pytest.raises(ValueError, match="End time cannot be earlier or equal than start time"):
            service.create_flash_sale(db_session, name="Sale", start_time=start, end_time=end)

    def test_create_overlapping_raises(self, db_session):
        _make_flash_sale(db_session, name="Existing Sale", days_offset=0, duration_days=5)

        start = _today() + timedelta(days=1)
        end = start + timedelta(days=3)

        with pytest.raises(ValueError, match="overlaps with existing flash sale"):
            service.create_flash_sale(db_session, name="New Sale", start_time=start, end_time=end)

    def test_create_non_overlapping_succeeds(self, db_session):
        _make_flash_sale(db_session, name="First Sale", days_offset=0, duration_days=2)

        start = _today() + timedelta(days=3)
        end = start + timedelta(days=2)

        service.create_flash_sale(db_session, name="Second Sale", start_time=start, end_time=end)

        count = db_session.query(models.FlashSale).count()
        assert count == 2


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
#  get_active_flash_sale
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class TestGetActiveFlashSale:
    def test_get_active_success(self, db_session):
        _make_flash_sale(db_session, name="Active Sale", days_offset=-1, duration_days=3)

        result = service.get_active_flash_sale(db_session)
        assert result is not None
        assert result.name == "Active Sale"

    def test_get_active_not_found_raises(self, db_session):
        with pytest.raises(NotFoundError):
            service.get_active_flash_sale(db_session)

    def test_get_active_ignores_future_sale(self, db_session):
        _make_flash_sale(db_session, name="Future Sale", days_offset=10, duration_days=2)

        with pytest.raises(NotFoundError):
            service.get_active_flash_sale(db_session)

    def test_get_active_ignores_past_sale(self, db_session):
        _make_flash_sale(db_session, name="Past Sale", days_offset=-10, duration_days=2)

        with pytest.raises(NotFoundError):
            service.get_active_flash_sale(db_session)


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
#  update_flash_sale
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class TestUpdateFlashSale:
    def test_update_success(self, db_session):
        fs = _make_flash_sale(db_session, name="Old Name", days_offset=0, duration_days=3)

        new_start = _today()
        new_end = new_start + timedelta(days=5)
        service.update_flash_sale(
            db_session,
            id=fs.id,
            name="New Name",
            start_time=new_start,
            end_time=new_end,
        )

        updated = db_session.get(models.FlashSale, fs.id)
        assert updated.name == "New Name"
        assert updated.end_time == new_end

    def test_update_not_found_raises(self, db_session):
        with pytest.raises(NotFoundError):
            service.update_flash_sale(
                db_session,
                id=9999,
                name="X",
                start_time=_today(),
                end_time=_today() + timedelta(days=2),
            )

    def test_update_empty_name_raises(self, db_session):
        fs = _make_flash_sale(db_session, days_offset=0, duration_days=3)

        with pytest.raises(ValueError, match="Name cannot be empty"):
            service.update_flash_sale(
                db_session,
                id=fs.id,
                name="",
                start_time=_today(),
                end_time=_today() + timedelta(days=2),
            )

    def test_update_overlapping_raises(self, db_session):
        _make_flash_sale(db_session, name="Other Sale", days_offset=5, duration_days=3)
        fs = _make_flash_sale(db_session, name="My Sale", days_offset=0, duration_days=2)

        with pytest.raises(ValueError, match="overlaps with existing flash sale"):
            service.update_flash_sale(
                db_session,
                id=fs.id,
                name="My Sale Updated",
                start_time=_today() + timedelta(days=4),
                end_time=_today() + timedelta(days=7),
            )


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
#  change_active_flash_sale
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class TestChangeActiveFlashSale:
    def test_toggle_active_to_inactive(self, db_session):
        fs = _make_flash_sale(db_session, is_active=True)

        service.change_active_flash_sale(db_session, id=fs.id)

        updated = db_session.get(models.FlashSale, fs.id)
        assert updated.is_active is False

    def test_toggle_inactive_to_active(self, db_session):
        fs = _make_flash_sale(db_session, is_active=False)

        service.change_active_flash_sale(db_session, id=fs.id)

        updated = db_session.get(models.FlashSale, fs.id)
        assert updated.is_active is True

    def test_change_active_not_found_raises(self, db_session):
        with pytest.raises(NotFoundError):
            service.change_active_flash_sale(db_session, id=9999)


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
#  delete_flash_sale
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class TestDeleteFlashSale:
    def test_delete_success(self, db_session):
        fs = _make_flash_sale(db_session, name="To Delete")

        service.delete_flash_sale(db_session, id=fs.id)

        assert db_session.get(models.FlashSale, fs.id) is None

    def test_delete_not_found_raises(self, db_session):
        with pytest.raises(NotFoundError):
            service.delete_flash_sale(db_session, id=9999)

    def test_delete_does_not_affect_others(self, db_session):
        fs1 = _make_flash_sale(db_session, name="Keep", days_offset=0, duration_days=2)
        fs2 = _make_flash_sale(db_session, name="Delete", days_offset=5, duration_days=2)

        service.delete_flash_sale(db_session, id=fs2.id)

        assert db_session.get(models.FlashSale, fs1.id) is not None
        assert db_session.query(models.FlashSale).count() == 1
