from atexit import register
from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(BillingAddress)
admin.site.register(RedeemCode)
admin.site.register(Payment)




         