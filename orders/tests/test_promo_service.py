# orders/tests/test_promo_service.py
import pytest
from orders.services.promo_service import apply_promo_code
from django.utils import timezone
from orders.models import PromoCodeUsage

@pytest.mark.django_db
def test_apply_valid_promo(user, product, promo):
    items = [{"product": product, "quantity": 2}]

    result = apply_promo_code(user, "TEST10", items)

    assert result["discount_percent"] == promo.discount_percent
    assert result["items"][0]["discount"] > 0



@pytest.mark.django_db
def test_expired_promo(user, product, promo):
    promo.active_to = timezone.now() - timezone.timedelta(days=1)
    promo.save()

    items = [{"product": product, "quantity": 1}]

    with pytest.raises(Exception):
        apply_promo_code(user, "TEST10", items)



@pytest.mark.django_db
def test_promo_already_used(user, product, promo):
    PromoCodeUsage.objects.create(user=user, promo_code=promo)

    items = [{"product": product, "quantity": 1}]

    with pytest.raises(Exception):
        apply_promo_code(user, "TEST10", items)