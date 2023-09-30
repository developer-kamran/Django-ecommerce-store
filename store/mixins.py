from django.shortcuts import render, redirect
from decimal import Decimal
from django.contrib import messages
from .models import *
from .forms import *

class BaseMixin():
    def get_order(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order
        except Order.DoesNotExist:
            try:
                order = Order.objects.get(user=self.request.user, ordered=True, delivered=False)
                return order
            except Order.DoesNotExist:
                return None

    def get_billing_address(self):
        return BillingAddress.objects.filter(user=self.request.user).last()


class OrderCheckMixin(BaseMixin):
    def check_order(self):
        order = self.get_order()
        if not order:
            messages.error(self.request, "You have no active order. Please add items before proceeding")
            return False

        if not order.items.exists():
            messages.error(self.request, "Your cart is currently empty. Please add items before proceeding")
            return False

        return True


class CheckoutMixin(OrderCheckMixin):
    def get(self, *args, **kwargs):
        if not self.check_order():
            return redirect('store:home')

        order = self.get_order()
        if order.billing_address and not order.ordered :
            messages.info(self.request, "You have already completed the checkout. No further action is needed.")
            return redirect('store:payment')
        if order.ordered :
            return redirect('store:success')

        form = None
        billing_address = self.get_billing_address()

        if billing_address and billing_address.save_info:
            billing_address.instructions = None  # Reset the instructions to None
            billing_address.save()
            form = CheckoutForm(instance=billing_address)
        else:
            form = CheckoutForm()

        context = {'form': form, 'order': order}
        return render(self.request, 'store/checkout_page.html', context)


class PaymentMixin(OrderCheckMixin):
    def get_discount_amount(self, order):
        discount_amount = Decimal(0)
        if order.has_redeemed:
            for order_item in order.items.all():
                discount_amount += order_item.get_final_price() * Decimal('0.05')

        return discount_amount.quantize(Decimal('0.00'))

    def get(self, request, *args, **kwargs):
        if not self.check_order():
            return redirect('store:home')

        order = self.get_order()
        if not order.billing_address:
            messages.error(request, "Please complete the checkout process first.")
            return redirect('store:checkout')
        if order.ordered:
            return redirect('store:success')

        discount_amount = self.get_discount_amount(order)

        return render(request, 'store/payment.html', {
            'order': order,
            'has_redeemed': order.has_redeemed,
            'discount_amount': discount_amount,
        })

