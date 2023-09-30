# Django imports
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.views.generic import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Local imports
from .forms import*
from .models import *
from .utils import generate_order_id, redirect_to_payment_with_error
from .decorators import have_active_order,login_required_with_message
from .mixins import *

# Third-party imports
from django.db.models.functions import Random
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'store/home.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        random_items = queryset.order_by(Random())
        return random_items


class ItemDetailView( DetailView):
    model = Item
    template_name = 'store/product.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()
        is_in_cart = False

        if self.request.user.is_authenticated:
            order = self.request.user.order_set.filter(ordered=False).first()
            if order:
                is_in_cart = order.items.filter(item=item).exists()

        context['is_in_cart'] = is_in_cart
        return context


@login_required_with_message("Please login to add items to the cart.", "store:checkout")
@have_active_order
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order = Order.objects.filter(user=request.user, ordered=False).first()

    if order and order.items.filter(item__slug=item.slug).exists():
        order_item.quantity += 1
        order_item.save()
        messages.info(request, "Item quantity updated.")

    else:
        if not order:
            order = Order.objects.create(user=request.user, ordered_date=timezone.now())
        order.items.add(order_item)
        messages.success(request, "Item added to the cart.")

    return redirect("store:order-summary")


@login_required
@have_active_order
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = Order.objects.filter(user=request.user, ordered=False).first()

    if order:
        order_item = order.items.filter(item=item, user=request.user, ordered=False).first()
        if order_item:
            order_item.delete()
            messages.error(request, "Item removed from the cart") 

    return redirect("store:order-summary")


@login_required
@have_active_order
def decrease_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False).first()
    if order_item:
        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
        else:
            order_item.delete()  # Delete the order item from the database
        messages.info(request, "Item's quantity updated")
        return redirect("store:order-summary")


class Cart(LoginRequiredMixin, View):
    context = {} 

    def get(self, *args, **kwargs):
        context = {}
        try:
            try:
                order = Order.objects.get(user=self.request.user, ordered=False, delivered=False)
                context = {'order': order}

            except Order.DoesNotExist:
                order = Order.objects.get(user=self.request.user, ordered=True, delivered=False)
                return redirect('store:success')

        except Order.DoesNotExist:
            pass  # You can choose to handle this case if necessary

        return render(self.request, 'store/order_summary.html', context)


class CheckoutView(LoginRequiredMixin,CheckoutMixin,View):

    def post(self, request, *args, **kwargs):
        form =CheckoutForm(request.POST )
        order = Order.objects.get(user=self.request.user, ordered=False)

        if form.is_valid():
            billing_address = form.save(commit= False)
            billing_address.user = self.request.user
            billing_address.save()

            order.billing_address = billing_address
            order.save()
            return redirect('store:payment')

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(self.request, f"{field.capitalize()}: {error}")

            return redirect('store:checkout')


class PaymentView(LoginRequiredMixin,PaymentMixin,View):

    def post(self, request, *args, **kwargs):
        token = request.POST.get('stripeToken')
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            amount = 0
            if order.has_redeemed:
                amount = order.grand_total_with_redeem()
            else:
                amount = order.grand_total()
            amount = int(amount*100)
            
            # Create a charge using Stripe API
            charge = stripe.Charge.create(
                    amount=amount,
                    currency='usd',
                    source=token,
            )

            # Create a payment record
            payment = Payment.objects.create(
                stripe_charge_id=charge['id'],
                user=request.user,
                amount=amount
            )
 
            # Mark order items as ordered
            order_items = order.items.all()
            for item in order_items:
                item.ordered = True
                item.save()

            # Update order status and payment information
            order.ordered = True
            order.payment = payment
            order.order_id = generate_order_id()
            order.save()
            return redirect('store:success')

        except stripe.error.CardError as e:
        # Handle card error
            error_message = e.error.message
            return redirect_to_payment_with_error(self,error_message)

        except stripe.error.RateLimitError as e:
            error_message = "We're experiencing high traffic at the moment. Please try again later."
            return redirect_to_payment_with_error(self,error_message)

        except stripe.error.InvalidRequestError as e:
            error_message = "Invalid request. Please try again."
            return redirect_to_payment_with_error(self,error_message)

        except stripe.error.AuthenticationError as e:
            error_message = "Authentication with Stripe failed. Please contact support."
            return redirect_to_payment_with_error(self,error_message)

        except stripe.error.APIConnectionError as e:
            error_message = "Network error occurred. Please check your internet connection and try again."
            return redirect_to_payment_with_error(self,error_message)

        except stripe.error.StripeError as e:
            error_message = 'An error occurred during payment processing. Please try again later.'
            return redirect_to_payment_with_error(self,error_message)

        except Exception as e:
            error_message = 'A serious error occurred. Please contact support.'
            order.ordered = False
            order_items = order.items.all()
            for item in order_items:
                item.ordered = False
                item.save()
            order.save()
            return redirect_to_payment_with_error(self,error_message)

        except Order.DoesNotExist:
            messages.error(request, "Order does not exist. You don't have any active order.")
            return redirect('/')


def redeem_code(request):
    if request.method == 'POST':
        redeem_code = request.POST.get('redeem_code')  # Get the redeem code from the form
        try:
            redeem = RedeemCode.objects.get(code=redeem_code, is_valid=True,is_used= False)
            order = Order.objects.get(user=request.user, ordered=False)
            # Mark the redeem code as used
            redeem.is_used = True
            redeem.save()

            # Set the has_redeemed flag in the order
            order.has_redeemed = True
            order.save()

            messages.success(request, 'Redeem code applied successfully.')
            return redirect('store:payment')
                
        except RedeemCode.DoesNotExist:
            messages.error(request, 'Invalid redeem code. Please try again.')

    return redirect('store:payment')


class SuccessView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        context = {}
        order = None
        try:
            order = Order.objects.get(user=request.user, ordered=True, delivered=False)

        except Order.DoesNotExist:
            return redirect('store:home')

        ordered_items = order.items.all()
        context = {'ordered_items': ordered_items,'order':order}
        return render(request, 'store/success.html', context)
    
        



def error_404(request, exception):
    return render(request, 'store/error.html', status=404)
