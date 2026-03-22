from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from orders.serializers import (
    OrderCreateSerializer,
    OrderOutputSerializer
)
from orders.services.order_service import create_order
from orders.services.promo_service import PromoCodeError

User = get_user_model()

class OrderCreateView(APIView):

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        
        try:
            user = User.objects.get(id=data["user_id"])
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            order = create_order(
                user=user,
                items_data=data["goods"],
                promo_code_str=data.get("promo_code")
            )

        except PromoCodeError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        response_data = {
            "user_id": order.user.id,
            "order_id": order.id,
            "goods": [
                {
                    "good_id": item.product.id,
                    "quantity": item.quantity,
                    "price": item.price,
                    "discount": item.discount,
                    "total": item.total,
                }
                for item in order.items.all()
            ],
            "price": order.price,
            "discount": order.discount,
            "total": order.total,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)