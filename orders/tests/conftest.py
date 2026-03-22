# orders/tests/conftest.py
import pytest
from django.contrib.auth import get_user_model
from orders.models import Product, Category, PromoCode
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(username="test", password="123")


@pytest.fixture
def category():
    return Category.objects.create(name="Food")


@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Apple",
        price=100,
        category=category
    )


@pytest.fixture
def promo(category):
    now = timezone.now()
    promo = PromoCode.objects.create(
        code="TEST10",
        discount_percent=10,
        active_from=now - timedelta(days=1),
        active_to=now + timedelta(days=1),
        max_uses=10
    )
    promo.categories.add(category)
    return promo