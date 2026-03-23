from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from orders.models import Product, Category, PromoCode


class Command(BaseCommand):
    help = "Заполняет БД тестовыми данными"

    def handle(self, *args, **kwargs):

        user, _ = User.objects.get_or_create(username="test_user")

        food, _ = Category.objects.get_or_create(name="Food")
        tech, _ = Category.objects.get_or_create(name="Tech")

        Product.objects.get_or_create(
            name="Apple",
            price=Decimal("100"),
            category=food,
        )

        Product.objects.get_or_create(
            name="Laptop",
            price=Decimal("1000"),
            category=tech,
        )

        PromoCode.objects.get_or_create(
            code="TEST10",
            discount_percent=10,
            max_uses=100,
            active_from=timezone.now(),
            active_to=timezone.now() + timedelta(days=30),
        )

        self.stdout.write(self.style.SUCCESS("Database filled"))
