from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps
from .models import *

def have_active_order(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        order = Order.objects.filter(user=user, ordered=True, delivered=False).first()
        if order is not None:
            messages.info(request, "You already have an active order to be delivered. Please await the delivery before placing another order.")
            return redirect('store:home')
        return view_func(request, *args, **kwargs)
    return wrapper
    

def login_required_with_message(message, next_url):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.info(request, message)
                return redirect(next_url)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
