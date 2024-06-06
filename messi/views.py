from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse
def leo(request):
    return HttpResponse('LIGY')

# Create your views here.
def index(request):
    return render(request,"index.html")


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        mobile = request.POST['mobile']
        location = request.POST['location']
        
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error_message': 'Username already exists.'})
        
        user = User.objects.create_user(username=username, password=password, email=email)
        
        # Create UserProfile object and set additional fields
        profile = UserProfile.objects.create(user=user, mobile=mobile, location=location)
        
        login(request, user)
        return redirect('login')
       
    return render(request, 'signup.html')
from .models import  UserProfile,CartItem,Order,OrderItem
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Add session variables
            request.session['username'] = username
            request.session['user_id'] = user.id
            
            return redirect('index')  # Replace 'index' with your desired redirect URL
        else:
            return render(request, 'login.html', {'error_message': 'Invalid username or password.'})
    return render(request, 'login.html')

def product(request):
    return render(request, 'product.html')
from .models import Product
from .forms import ProductForm,BillingDetails

def upload_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=form.instance.pk)
    else:
        form = ProductForm()
    return render(request, 'upload_product.html', {'form': form})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})
from django.contrib.auth import logout
def user_logout(request):
    logout(request)
    return redirect('index')  

from django.contrib.auth.decorators import login_required
@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)  # Filter cart items for the logged-in user
    total_quantity = sum(item.quantity for item in cart_items)
    total_price = sum(item.total() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_quantity': total_quantity, 'total_price': total_price})


from django.contrib import messages

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id, user=request.user)
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        if quantity.isdigit() and int(quantity) > 0:
            cart_item.quantity = int(quantity)
            cart_item.save()
    return redirect('cart')

from .forms import BillingDetailsForm


def checkout(request):
    if request.method == 'POST':
        form = BillingDetailsForm(request.POST)
        if form.is_valid():
            user = request.user
            billing_details, created = BillingDetails.objects.get_or_create(user=user)
            if not created:
                # If billing details already exist, update them with the form data
                billing_details.name = form.cleaned_data['name']
                billing_details.phone_number = form.cleaned_data['phone_number']
                billing_details.email = form.cleaned_data['email']
                billing_details.address = form.cleaned_data['address']
                billing_details.postal_code = form.cleaned_data['postal_code']
                billing_details.company_name = form.cleaned_data['company_name']
                billing_details.save()

            # Process the order
            cart_items = CartItem.objects.filter(user=user)
            total_price = sum(item.total() for item in cart_items)
            order = Order.objects.create(user=user, total_price=total_price)
            for cart_item in cart_items:
                OrderItem.objects.create(order=order, cart_item=cart_item, quantity=cart_item.quantity)
            cart_items.delete()  # Clear the cart after placing the order

            return redirect('order_confirmation', order_id=order.id)
    else:
        form = BillingDetailsForm()
    
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total() for item in cart_items)
    return render(request, 'checkout.html', {'form': form, 'cart_items': cart_items, 'total_price': total_price})








def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'order_confirmation.html', {'order': order})

from django.conf import settings

from django.http import JsonResponse
from .models import Order

import razorpay
from django.conf import settings

client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))



import razorpay
from django.conf import settings

client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

from django.shortcuts import redirect

def razorpay_payment(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        total_amount = order.total_price  # Assuming you have a field 'total_price' in your Order model
        # Create a Razorpay payment object here and return the response
        # After successful payment, redirect to the receipt URL
        return redirect('receipt',order_id=order_id)
    return JsonResponse({'error': 'Invalid Request'})

from django.shortcuts import render
from django.http import JsonResponse
from messi.models import CartItem  # Import your CartItem model

def cart_count(request):
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    else:
        cart_count = 0

    return JsonResponse({'cart_count': cart_count})
