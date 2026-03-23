# orders/tests/test_order_api.py
import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_create_order_with_promo(user, product, promo):
    client = APIClient()

    data = {
        "user_id": user.id,
        "goods": [{"product_id": product.id, "quantity": 2}],
        "promo_code": "TEST10",
    }

    response = client.post("/api/orders/", data, format="json")

    assert response.status_code == 201
    assert response.data["total"] < response.data["price"]


@pytest.mark.django_db
def test_create_order_without_promo(user, product):
    client = APIClient()

    data = {"user_id": user.id, "goods": [{"product_id": product.id, "quantity": 1}]}

    response = client.post("/api/orders/", data, format="json")

    assert response.status_code == 201
    assert response.data["price"] == response.data["total"]


@pytest.mark.django_db
def test_invalid_product(user):
    client = APIClient()

    data = {"user_id": user.id, "goods": [{"product_id": 999, "quantity": 1}]}

    response = client.post("/api/orders/", data, format="json")

    assert response.status_code == 400
