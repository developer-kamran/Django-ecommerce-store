from django.shortcuts import render, redirect
from django.contrib import messages
from random import randint

def upload_to(instance,filename):
    return f'images/{filename}'

def generate_order_id():
    from .models import Order
    while True:
        order_id = ''.join(str(randint(0, 9)) for _ in range(5))
        if not Order.objects.filter(order_id=order_id).exists():
            break
    return order_id

def redirect_to_payment_with_error(self,  error_message):
    messages.error(self.request, error_message)
    return redirect('store:payment')
    
def render_with_errors(request, error_message, email):
    return render(request, 'store/login_register.html', {
        'page': 'login',
        'error_message': error_message,
        'email': email,
    })


