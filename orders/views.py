from django.shortcuts import render

# Create your views here.
# orders/views.py
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse

from orders.models import Order
from orders.serializers import (
    OrderCreateSerializer,
    OrderOutputSerializer,
    OrderItemOutputSerializer,
)
from orders.services.order_service import create_order
from orders.services.promo_service import PromoCodeError

User = get_user_model()


@extend_schema(
    summary="Создать заказ",
    description="Создает заказ с применением промокода",
    request=OrderCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=OrderOutputSerializer, description="Заказ успешно создан"
        ),
        400: OpenApiResponse(description="Ошибка валидации или промокод"),
        404: OpenApiResponse(description="Пользователь не найден"),
    },
)
class OrderCreateView(APIView):

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            user = User.objects.get(id=data["user_id"])
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            order = create_order(
                user=user,
                items_data=data["goods"],
                promo_code_str=data.get("promo_code"),
            )
        except PromoCodeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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


@extend_schema(
    summary="Список заказов",
    description="Возвращает список всех заказов",
    responses={200: OrderOutputSerializer(many=True)},
)
class OrderListView(APIView):

    def get(self, request):
        orders = Order.objects.all()
        response_data = []

        for order in orders:
            response_data.append(
                {
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
            )

        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Получить заказ по ID",
    description="Возвращает данные одного заказа по его ID",
    responses={
        200: OrderOutputSerializer,
        404: OpenApiResponse(description="Заказ не найден"),
    },
)
class OrderDetailView(APIView):

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
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

        return Response(response_data, status=status.HTTP_200_OK)
