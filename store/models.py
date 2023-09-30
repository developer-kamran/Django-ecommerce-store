from django.urls import reverse
from django.utils import timezone
from decimal import Decimal,ROUND_DOWN
from django.utils.text import slugify
from .utils import upload_to
from django_countries.fields import CountryField
from django.contrib.auth.models import User
from django.db import models

CATEGORY_CHOICES=[
    ('S','Shirt'),
    ('SW','Shirt Wear'),
    ('OW','Outwear'),
]

LABEL_CHOICES=[
    ('P','primary'),
    ('S','secondary'),
    ('D','danger'),
]

class Item(models.Model):
    title=models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True, blank=True)
    description=models.TextField()
    image=models.ImageField(blank=True,null=True,upload_to=upload_to)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price=models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    category=models.CharField(choices=CATEGORY_CHOICES,max_length=2)
    label=models.CharField(choices=LABEL_CHOICES,max_length=1)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:  # Generate slug only if it's not set
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("store:product",kwargs={
            'slug':self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("store:add-to-cart",kwargs={
            'slug':self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("store:remove-from-cart",kwargs={
            'slug':self.slug
        })


class OrderItem(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    item=models.ForeignKey(Item,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    ordered=models.BooleanField(default=False)

    def __str__(self):
        order_number = self.get_order_number()
        status = "incomplete" if not self.get_order_status() else "completed"
        return f"Order no {order_number} ({status}): {self.quantity} of {self.item.title}"

    def get_order_number(self):
        order = Order.objects.filter(items=self).first()
        if order:
            order_number = order.pk
        else:
            order_number = "N/A"
        return order_number

    def get_order_status(self):
        order = Order.objects.filter(items=self).first()
        if order:
            return order.ordered
        return False

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_discounted_price(self):
        if self.item.discount_price:
            return self.quantity * self.item.discount_price
        return Decimal(0)

    def get_amount_save(self):
        return self.get_total_item_price() - self.get_discounted_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.quantity * self.item.discount_price
        return self.get_total_item_price()


class Order(models.Model):
    order_id = models.CharField(max_length=5, unique=True,null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    items=models.ManyToManyField(OrderItem)
    start_date=models.DateTimeField(auto_now_add=True)
    ordered_date=models.DateTimeField(default=timezone.now)
    ordered=models.BooleanField(default=False)
    has_redeemed = models.BooleanField(default=False)
    billing_address=models.ForeignKey('BillingAddress',on_delete=models.SET_NULL,null=True,blank=True)
    payment=models.ForeignKey('Payment',on_delete=models.SET_NULL,null=True,blank=True)
    delivered = models.BooleanField(default=False, blank=True, null=False)

    def __str__(self):
        order_status = "Completed" if self.ordered else "Not Completed"
        delivery_status = "Delivered" if self.delivered else "Not Delivered"

        return f"{self.user.username} Order ID# ({self.order_id}) ({order_status}) ({delivery_status})"


    def grand_total(self):
        return sum(order_item.get_final_price() for order_item in self.items.all())

    def grand_total_with_redeem(self):
        total = self.grand_total()
        if self.has_redeemed:
            total -= total * Decimal('0.05')
        return total.quantize(Decimal('0.00'), rounding=ROUND_DOWN)


class RedeemCode(models.Model):
    code = models.CharField(max_length=6, unique=True)
    is_valid = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)  

    def __str__(self):
        code_used = '(Used)' if self.is_used else ''
        return f"{self.code} {code_used}"


class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.CharField(max_length=30)
    address = models.CharField(max_length=256)
    phone_no= models.CharField(max_length=14)
    zip = models.CharField(max_length=10,null=True,blank=True)
    country = CountryField(multiple=False)
    city = models.CharField(max_length=100, null=False, blank=False)
    instructions = models.TextField(blank=True, null=True)
    save_info = models.BooleanField(blank=True, null=False, default= False)

    def __str__(self):
        return f'Billing address of {self.user.username}'


class Payment(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
    stripe_charge_id=models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username