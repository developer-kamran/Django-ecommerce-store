# Django imports
from django.contrib import messages
from django.views.generic import *
from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate,logout

# Local imports
from .forms import*
from .models import *
from .utils import render_with_errors


def registerUser(request):
    if request.user.is_authenticated:
        return redirect('store:home')

    form = CustomUserForm()

    if request.method == 'POST':
        form = CustomUserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            messages.success(request, "Registration successful!  Start exploring our products and enjoy your shopping experience!")
            return redirect('store:home')
        else:
            messages.error(request, "Oops! An error occurred during registration. Please double-check your information and try again.")

    return render(request, 'store/login_register.html', {'form': form})


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            error = 'The email you entered does not exist. Please make sure to enter the correct email address.'
            return render_with_errors(request, error, email)

        if user.check_password(password):
            login(request, user)

            pending_order = Order.objects.filter(user=user, ordered=False, delivered=False,items__isnull=False)
            undelivered_order = Order.objects.filter(user=user, ordered=True, delivered=False)

            if undelivered_order:
                messages.info(request, "Welcome back! Your order is being prepared for delivery. Sit tight, it'll be with you soon!")
                return redirect('store:success') 
            if pending_order:
                messages.info(request, "Welcome back! You have an ongoing order in progress. Finish your purchase to proceed.")
                return redirect('store:order-summary') 

            messages.success(request, "Welcome back! You have successfully logged in. Enjoy your shopping experience!") 
            return redirect('store:home')

        else:
            error = 'The password you entered is incorrect. Please try again.'
            return render_with_errors(request, error, email)

    return render(request, 'store/login_register.html',{'page':page})


def logoutUser(request):
    logout(request)
    messages.info(request, "You have been logged out. We hope to see you again soon!")
    return redirect('store:login')
