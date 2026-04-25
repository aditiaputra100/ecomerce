import pytest
from datetime import datetime, timedelta, timezone

from app.campaign import service, models
from app.exceptions import NotFoundError


# === Helper ===

def _today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def _make_campaign(db, name="Campaign", days_offset=0, duration_days=2, is_active=True):
    """Insert a Campaign directly into the DB and return it."""
    start = _today() + timedelta(days=days_offset)
    end = start + timedelta(days=duration_days)
    campaign = models.Campaign(
        name=name,
        start_time=start,
        end_time=end,
        is_active=is_active,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


# ═══════════════════════════════════════════════════════════════════════════
#  create_campaign
# ═══════════════════════════════════════════════════════════════════════════

class TestCreateCampaign:
    def test_create_success(self, db_session):
        start = _today()
        end = start + timedelta(days=3)

        result = service.create_campaign(
            db_session,
            name="Year End Sale",
            start_time=start,
            end_time=end,
        )

        assert result is not None
        assert result.name == "Year End Sale"
        assert result.is_active is False

    def test_create_empty_name_raises(self, db_session):
        start = _today()
        end = start + timedelta(days=3)

        with pytest.raises(ValueError, match="Name cannot be empty"):
            service.create_campaign(db_session, name="  ", start_time=start, end_time=end)

    def test_create_start_time_in_past_raises(self, db_session):
        start = _today() - timedelta(days=1)
        end = start + timedelta(days=3)

        with pytest.raises(ValueError, match="Start time cannot be earlier than today"):
            service.create_campaign(db_session, name="Sale", start_time=start, end_time=end)

    def test_create_end_time_equal_start_raises(self, db_session):
        start = _today()
        end = start  # same date

        with pytest.raises(ValueError, match="End time cannot be earlier or equal than start time"):
            service.create_campaign(db_session, name="Sale", start_time=start, end_time=end)

    def test_create_end_time_before_start_raises(self, db_session):
        start = _today() + timedelta(days=5)
        end = _today()

        with pytest.raises(ValueError, match="End time cannot be earlier or equal than start time"):
            service.create_campaign(db_session, name="Sale", start_time=start, end_time=end)

    def test_create_overlapping_raises(self, db_session):
        _make_campaign(db_session, name="Existing Sale", days_offset=0, duration_days=5)

        start = _today() + timedelta(days=1)
        end = start + timedelta(days=3)

        with pytest.raises(ValueError, match="overlaps with existing campaign"):
            service.create_campaign(db_session, name="New Sale", start_time=start, end_time=end)

    def test_create_non_overlapping_succeeds(self, db_session):
        _make_campaign(db_session, name="First Sale", days_offset=0, duration_days=2)

        start = _today() + timedelta(days=3)
        end = start + timedelta(days=2)

        result = service.create_campaign(db_session, name="Second Sale", start_time=start, end_time=end)

        count = db_session.query(models.Campaign).count()
        assert count == 2
        assert result.name == "Second Sale"


# ═══════════════════════════════════════════════════════════════════════════
#  get_active_campaign
# ═══════════════════════════════════════════════════════════════════════════

class TestGetActiveCampaign:
    def test_get_active_success(self, db_session):
        _make_campaign(db_session, name="Active Sale", days_offset=-1, duration_days=3)

        result = service.get_active_campaign(db_session)
        assert result is not None
        assert len(result) == 1
        assert result[0].name == "Active Sale"

    def test_get_active_empty(self, db_session):
        result = service.get_active_campaign(db_session)
        assert result == []

    def test_get_active_ignores_future_sale(self, db_session):
        _make_campaign(db_session, name="Future Sale", days_offset=10, duration_days=2)

        result = service.get_active_campaign(db_session)
        assert result == []

    def test_get_active_ignores_past_sale(self, db_session):
        _make_campaign(db_session, name="Past Sale", days_offset=-10, duration_days=2)

        result = service.get_active_campaign(db_session)
        assert result == []


# ═══════════════════════════════════════════════════════════════════════════
#  update_campaign
# ═══════════════════════════════════════════════════════════════════════════

class TestUpdateCampaign:
    def test_update_success(self, db_session):
        campaign = _make_campaign(db_session, name="Old Name", days_offset=0, duration_days=3)

        new_start = _today()
        new_end = new_start + timedelta(days=5)
        result = service.update_campaign(
            db_session,
            id=campaign.id,
            name="New Name",
            start_time=new_start,
            end_time=new_end,
        )

        assert result.name == "New Name"
        assert result.end_time == new_end

    def test_update_not_found_raises(self, db_session):
        with pytest.raises(NotFoundError):
            service.update_campaign(
                db_session,
                id=9999,
                name="X",
                start_time=_today(),
                end_time=_today() + timedelta(days=2),
            )

    def test_update_empty_name_raises(self, db_session):
        campaign = _make_campaign(db_session, days_offset=0, duration_days=3)

        with pytest.raises(ValueError, match="Name cannot be empty"):
            service.update_campaign(
                db_session,
                id=campaign.id,
                name="",
                start_time=_today(),
                end_time=_today() + timedelta(days=2),
            )

    def test_update_overlapping_raises(self, db_session):
        _make_campaign(db_session, name="Other Sale", days_offset=5, duration_days=3)
        campaign = _make_campaign(db_session, name="My Sale", days_offset=0, duration_days=2)

        with pytest.raises(ValueError, match="overlaps with existing campaign"):
            service.update_campaign(
                db_session,
                id=campaign.id,
                name="My Sale Updated",
                start_time=_today() + timedelta(days=4),
                end_time=_today() + timedelta(days=7),
            )


# ═══════════════════════════════════════════════════════════════════════════
#  change_active_campaign
# ═══════════════════════════════════════════════════════════════════════════

class TestChangeActiveCampaign:
    def test_toggle_active_to_inactive(self, db_session):
        campaign = _make_campaign(db_session, is_active=True)

        result = service.change_active_campaign(db_session, id=campaign.id)

        assert result.is_active is False

    def test_toggle_inactive_to_active(self, db_session):
        campaign = _make_campaign(db_session, is_active=False)

        result = service.change_active_campaign(db_session, id=campaign.id)

        assert result.is_active is True

    def test_change_active_not_found_raises(self, db_session):
        with pytest.raises(NotFoundError):
            service.change_active_campaign(db_session, id=9999)

# ═══════════════════════════════════════════════════════════════════════════
#  delete_campaign
# ═══════════════════════════════════════════════════════════════════════════

class TestDeleteCampaign:
    def test_delete_inactive_campaign_without_items_success(self, db_session):
        """Campaign nonaktif tanpa produk — berhasil dihapus"""
        campaign = _make_campaign(db_session, name="To Delete", is_active=False)

        service.delete_campaign(db_session, id=campaign.id)

        assert db_session.get(models.Campaign, campaign.id) is None

    def test_delete_active_campaign_raises_error(self, db_session):
        """Campaign aktif — tidak bisa dihapus, harus dinonaktifkan dulu"""
        campaign = _make_campaign(db_session, name="Active Campaign", is_active=True)

        with pytest.raises(ValueError, match="Cannot delete an active campaign"):
            service.delete_campaign(db_session, id=campaign.id)

        # Pastikan campaign masih ada di database
        assert db_session.get(models.Campaign, campaign.id) is not None

    def test_delete_campaign_with_items_raises_error(self, db_session):
        """Campaign nonaktif TAPI memiliki produk — tidak bisa dihapus"""
        campaign = _make_campaign(db_session, name="Has Items", is_active=False)

        # Tambah CampaignItem ke campaign
        item = models.CampaignItem(
            campaign_id=campaign.id,
            product_id=1,  # ID produk dummy
            special_price=50000,
            stock_limit=10,
        )
        db_session.add(item)
        db_session.commit()

        with pytest.raises(ValueError, match="Cannot delete campaign that has registered products"):
            service.delete_campaign(db_session, id=campaign.id)

        # Pastikan campaign masih ada
        assert db_session.get(models.Campaign, campaign.id) is not None

    def test_delete_not_found_raises(self, db_session):
        """Campaign tidak ditemukan — raise NotFoundError"""
        with pytest.raises(NotFoundError):
            service.delete_campaign(db_session, id=9999)

    def test_delete_does_not_affect_others(self, db_session):
        """Menghapus satu campaign tidak menghapus campaign lainnya"""
        campaign1 = _make_campaign(db_session, name="Keep", is_active=False, days_offset=0, duration_days=2)
        campaign2 = _make_campaign(db_session, name="Delete", is_active=False, days_offset=5, duration_days=2)

        service.delete_campaign(db_session, id=campaign2.id)

        assert db_session.get(models.Campaign, campaign1.id) is not None
        assert db_session.query(models.Campaign).count() == 1
