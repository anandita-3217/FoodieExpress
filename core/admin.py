from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(DeliveryPartner)
admin.site.register(Order)
admin.site.register(OrderItem)


