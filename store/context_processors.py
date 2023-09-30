from .models import *

def header_data(request):
    order = None
    if request.user.is_authenticated:
        try:
            order = Order.objects.get(ordered=False, user=request.user)
        except Order.DoesNotExist:
            try:
                order = Order.objects.get(ordered=True, delivered=False, user=request.user)
            except Order.DoesNotExist:
                order = None
    return {
        'order': order,
    }
