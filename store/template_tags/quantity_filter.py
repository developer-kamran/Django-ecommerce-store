from django import template
from store.models import Order

register = template.Library()

@register.filter
def cart_items_quantity(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            cart_items = qs[0].items.all()
            total_quantity = sum(item.quantity for item in cart_items)
            return total_quantity
        return 0