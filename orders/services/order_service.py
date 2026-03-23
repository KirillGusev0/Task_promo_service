from decimal import Decimal
from django.db import transaction

from orders.models import Product, Order, OrderItem, PromoCodeUsage
from orders.services.promo_service import apply_promo_code


def create_order(user, items_data, promo_code_str=None):

    with transaction.atomic():

        product_ids = [item["product_id"] for item in items_data]

        products = Product.objects.filter(id__in=product_ids)

        product_map = {p.id: p for p in products}

        items = []

        for item in items_data:

            product = product_map.get(item["product_id"])

            if not product:
                raise ValueError(f"Product {item['product_id']} not found")

            quantity = item["quantity"]

            if quantity <= 0:
                raise ValueError("Quantity must be > 0")

            items.append(
                {
                    "product": product,
                    "quantity": quantity,
                }
            )

        total_price = Decimal("0")

        for item in items:
            total_price += item["product"].price * item["quantity"]

        promo_result = None

        if promo_code_str:

            promo_result = apply_promo_code(
                user=user, promo_code_str=promo_code_str, items=items
            )

            items = promo_result["items"]

        total_after_discount = Decimal("0")

        for item in items:

            product = item["product"]
            quantity = item["quantity"]

            discount_rate = item.get("discount_rate", Decimal("0"))
            discount_percent = item.get("discount_percent", Decimal("0"))

            line_price = product.price * quantity

            discount_amount = line_price * discount_rate

            line_total = line_price - discount_amount

            item["price"] = product.price
            item["discount_percent"] = discount_percent
            item["total"] = line_total

            total_after_discount += line_total

        order = Order.objects.create(
            user=user,
            promo_code=promo_result["promo"] if promo_result else None,
            price=total_price,
            discount=(
                promo_result["discount_percent"] if promo_result else Decimal("0")
            ),
            total=total_after_discount,
        )

        order_items = []

        for item in items:

            order_items.append(
                OrderItem(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    price=item["price"],
                    discount=item["discount_percent"],
                    total=item["total"],
                )
            )

        OrderItem.objects.bulk_create(order_items)

        if promo_result:

            PromoCodeUsage.objects.create(user=user, promo_code=promo_result["promo"])

            promo = promo_result["promo"]

            promo.used_count += 1
            promo.save(update_fields=["used_count"])

        return order
