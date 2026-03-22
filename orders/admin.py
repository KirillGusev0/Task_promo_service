from django.contrib import admin
from orders.models import *
# Register your models here.


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(PromoCode)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PromoCodeUsage)