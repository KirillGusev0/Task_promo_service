from decimal import Decimal
from django.utils import timezone

from orders.models import PromoCode, PromoCodeUsage

# =====================
# Exceptions
# =====================


class PromoCodeError(Exception):
    pass


class PromoCodeNotFound(PromoCodeError):
    pass


class PromoCodeExpired(PromoCodeError):
    pass


class PromoCodeUsageExceeded(PromoCodeError):
    pass


class PromoCodeAlreadyUsed(PromoCodeError):
    pass


# =====================
# Service
# =====================


def apply_promo_code(user, promo_code_str, items):

    now = timezone.now()

    try:
        promo = PromoCode.objects.get(code=promo_code_str)
    except PromoCode.DoesNotExist:
        raise PromoCodeNotFound("Promo code not found")

    if not (promo.active_from <= now <= promo.active_to):
        raise PromoCodeExpired("Promo code expired")

    if promo.used_count >= promo.max_uses:
        raise PromoCodeUsageExceeded("Promo code usage limit reached")

    if PromoCodeUsage.objects.filter(user=user, promo_code=promo).exists():
        raise PromoCodeAlreadyUsed("Promo code already used by this user")

    promo_categories = set(promo.categories.all())
    total_discount = Decimal("0")

    for item in items:

        product = item["product"]
        quantity = item["quantity"]

        item["discount_percent"] = Decimal("0")
        item["discount_rate"] = Decimal("0")
        item["discount"] = Decimal("0")

        if product.is_excluded_from_promos:
            continue

        if promo_categories and product.category not in promo_categories:
            continue

        discount_percent = promo.discount_percent
        discount_rate = discount_percent / Decimal("100")

        item["discount_percent"] = discount_percent
        item["discount_rate"] = discount_rate

        line_price = product.price * quantity
        discount_amount = line_price * discount_rate

        item["discount"] = discount_amount
        total_discount += discount_amount

    return {
        "promo": promo,
        "items": items,
        "total_discount": total_discount,
        "discount_percent": promo.discount_percent,
    }
