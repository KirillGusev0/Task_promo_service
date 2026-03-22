from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import CheckConstraint, Q

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    is_excluded_from_promos = models.BooleanField(default=False)

    def __str__(self):
        return self.name




class PromoCode(models.Model):

    code = models.CharField(max_length=50, unique=True)

    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    active_from = models.DateTimeField()
    active_to = models.DateTimeField()

    max_uses = models.PositiveIntegerField()
    used_count = models.PositiveIntegerField(default=0)

    categories = models.ManyToManyField(
        "Category",
        blank=True
    )

    def __str__(self):
        return self.code

    class Meta:
        constraints = [
            CheckConstraint(
                condition=Q(max_uses__gte=0),
                name="max_uses_positive"
            )
        ]




User = get_user_model()
class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    promo_code = models.ForeignKey(
        PromoCode,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

class PromoCodeUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE)

    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "promo_code")