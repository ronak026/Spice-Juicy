from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from .models import (
    Category,
    MenuItem,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Payment,
    Review,
    Address,
)
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, EmailAuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile, Address
from .forms import AddressForm
from .data import foods
from django.db.models import Q
import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    expensive_dish = MenuItem.objects.order_by('-price').first()
    top_dishes = MenuItem.objects.order_by('-price')[:10]
    
    return render(
        request,
        "home.html",
        {
            "expensive_dish": expensive_dish,
            "top_dishes": top_dishes,
        }
    )

def menu(request):
    query = request.GET.get("q", "")
    selected_category = request.GET.get("category", "")

    # Get all distinct category names from MenuItem
    categories = MenuItem.objects.values_list("category__name", flat=True).distinct()

    # Base queryset
    items = MenuItem.objects.filter(available=True)

    # Filter by category if selected
    if selected_category:
        items = items.filter(category__name=selected_category)

    # Search filter
    if query:
        items = items.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    context = {
        "items": items,
        "categories": categories,
        "selected_category": selected_category,
        "query": query,
    }
    return render(request, "menu.html", context)

# cart views
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    for item in cart_items:
        item.subtotal = item.menu_item.price * item.quantity
    total_price = sum([item.subtotal for item in cart_items])
    return render(
        request, "cart.html", {"cart_items": cart_items, "total_price": total_price}
    )


@login_required
def update_cart_quantity(request, cart_item_id):
    if request.method == "POST":
        cart_item = get_object_or_404(
            CartItem, id=cart_item_id, cart__user=request.user
        )
        quantity = int(request.POST.get("quantity", 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f"{cart_item.menu_item.name} quantity updated.")
        else:
            cart_item.delete()
            messages.info(request, f"{cart_item.menu_item.name} removed from cart.")
    return redirect("restaurant:view_cart")


# @login_required
# def add_to_cart(request, item_id):
#     menu_item = get_object_or_404(MenuItem, id=item_id)
#     cart, _ = Cart.objects.get_or_create(user=request.user)
#     cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)
#     if not created:
#         cart_item.quantity += 1
#         cart_item.save()
#     if not request.user.is_authenticated:
#         messages.error(request, "You need to be logged in to add items to your cart.")
#         return redirect("restaurant:login")
#     messages.success(request, f"Added {menu_item.name} to your cart.")
#     return redirect("restaurant:menu")

@login_required
def add_to_cart(request, item_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to add items to your cart.")
        return redirect("restaurant:login")

    menu_item = get_object_or_404(MenuItem, id=item_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"Added {menu_item.name} to your cart.")
    return redirect("restaurant:menu")

@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, menu_item_id=item_id)
    cart_item.delete()
    messages.success(request, f"Removed {cart_item.menu_item.name} from your cart.")
    return redirect("restaurant:view_cart")


@login_required
def place_order(request):
    # Get user's cart
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()

    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect("restaurant:menu")

    for item in cart_items:
        item.subtotal = item.menu_item.price * item.quantity

    address = Address.objects.filter(user=request.user).first()
    total_price = sum([item.subtotal for item in cart_items])

    if request.method == "POST":
        # Create order
        order = Order.objects.create(
            user=request.user, total_price=total_price, delivery_address=address
        )

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order, menu_item=item.menu_item, quantity=item.quantity
            )

        # Clear cart
        cart_items.delete()

        # Redirect to payment page instead of success page
        return redirect("restaurant:payment", order_id=order.id)

    # GET request — show summary page
    return render(
        request,
        "place_order.html",
        {"cart_items": cart_items, "total_price": total_price, "address": address},
    )



# Payment processing (mock)
@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method == "cod":
            # Handle Cash on Delivery
            order.status = "cod"
            order.save()
            return redirect("restaurant:order_success", order_id=order.id)

        elif payment_method == "stripe":
            # Stripe Checkout Session in INR
            success_url = request.build_absolute_uri(
                reverse("restaurant:order_success", kwargs={"order_id": order.id})
            )
            cancel_url = request.build_absolute_uri(
                reverse("restaurant:payment", kwargs={"order_id": order.id})
            )

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "inr",
                        "product_data": {"name": f"Order #{order.id}"},
                        "unit_amount": int(order.total_price * 100),  # amount in paise
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return redirect(checkout_session.url, code=303)

    return render(
        request,
        "payment.html",
        {"order": order, "stripe_public_key": settings.STRIPE_PUBLIC_KEY}
    )




# Order success page
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Mark order as paid
    if order.status != "preparing":
        order.status = "preparing"
        order.save()
        Payment.objects.create(order=order, amount=order.total_price, paid=True)

    return render(request, "order_success.html", {"order": order})




# Review submission
@login_required
def add_review(request, menu_item_id):
    menu_item = get_object_or_404(MenuItem, id=menu_item_id)
    if request.method == "POST":
        rating = int(request.POST.get("rating"))
        comment = request.POST.get("comment", "")
        Review.objects.create(
            user=request.user, menu_item=menu_item, rating=rating, comment=comment
        )
        return redirect("restaurant:menu")
    return render(request, "add_review.html", {"menu_item": menu_item})


# Address management
@login_required
def manage_address(request):
    # Check if user already has an address (optional — if you allow only one)
    try:
        address = Address.objects.get(user=request.user)
    except Address.DoesNotExist:
        address = None

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            addr.save()
            messages.success(request, "Your address has been saved successfully!")
            return redirect("restaurant:profile")
    else:
        form = AddressForm(instance=address)

    return render(request, "manage_address.html", {"form": form})


# registration and authentication views
def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully.")
            # login(request, user)  # Automatically log in the user after registration
            return redirect("restaurant:login")  # Redirect to login or any other page
        else:
            return render(request, "register.html", {"form": form})
    else:
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = EmailAuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            messages.success(request, "Logged in successfully.")
            login(request, user)  # Actually log the user in
            return redirect("restaurant:home")
        else:
            return render(request, "login.html", {"form": form})
    else:
        form = EmailAuthenticationForm()
    return render(request, "login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("restaurant:login")


# Profile and Profile Edit Views
@login_required
def profile(request):
    return render(request, "profile.html")


@login_required
def edit_profile(request):
    user = request.user
    # Ensure profile exists
    Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("restaurant:profile")  # Redirect to profile page
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=user.profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
    return render(request, "edit_profile.html", context)
