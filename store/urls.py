from django.urls import path
from django.conf.urls import handler404
from store.auth_views import *
from store.views import *

app_name = "store"

urlpatterns = [
    path('login/',loginPage,name="login"),
    path('logout/',logoutUser,name="logout"),
    path('register/',registerUser,name="register"),

    path('',HomeView.as_view(),name='home'),
    path('product/<str:slug>/',ItemDetailView.as_view(),name='product'),

    path('add_to_cart/<str:slug>/',add_to_cart,name='add-to-cart'),
    path('remove_from_cart/<str:slug>/',remove_from_cart,name='remove-from-cart'),
    path('decrease_from_cart/<str:slug>/',decrease_from_cart,name='decrease-from-cart'),

    path('order_summary/',Cart.as_view(),name='order-summary'),
    path('checkout/',CheckoutView.as_view(),name='checkout'),
    path('redeem_code/',redeem_code,name='redeem-code'),
    path('payment/',PaymentView.as_view(),name='payment'),
    path('success/',SuccessView.as_view(),name='success'),
]

handler404 = error_404

