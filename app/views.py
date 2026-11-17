from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Restaurant, Food, Order


def home(request):
    restaurants = Restaurant.objects.all()
    foods = Food.objects.filter(available=True).order_by("-id")[:8]

    return render(request, "home.html", {
        "restaurants": restaurants,
        "foods": foods,
    })


def menu(request):
    foods = Food.objects.filter(available=True)
    search_query = request.GET.get("q", "").strip()
    restaurant_id = request.GET.get("restaurant", "")

    if search_query:
        foods = foods.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(restaurant__rest_name__icontains=search_query)
        )

    if restaurant_id.isdigit():
        foods = foods.filter(restaurant_id=int(restaurant_id))

    restaurants = Restaurant.objects.all()

    return render(request, "menu.html", {
        "foods": foods,
        "restaurants": restaurants,
        "search_query": search_query,
        "selected_restaurant": restaurant_id,
    })


def food_detail(request, food_id):
    food = get_object_or_404(
        Food,
        id=food_id,
        available=True
    )

    return render(request, "food_detail.html", {
        "food": food,
    })


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            login(request, form.get_user())
            return redirect("home")
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


def user_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")

    return redirect("home")


@login_required
def add_to_cart(request, food_id):
    if request.method != "POST":
        return redirect("menu")

    food = get_object_or_404(
        Food,
        id=food_id,
        available=True
    )

    cart = request.session.get("cart", {})
    food_key = str(food.id)
    cart[food_key] = cart.get(food_key, 0) + 1

    request.session["cart"] = cart
    request.session.modified = True

    messages.success(request, f"{food.name} added to your cart.")
    return redirect("cart")


@login_required
def cart(request):
    cart_data = request.session.get("cart", {})
    cart_items = []
    grand_total = 0

    for food_id, quantity in cart_data.items():
        food = Food.objects.filter(
            id=food_id,
            available=True
        ).first()

        if food and isinstance(quantity, int) and quantity > 0:
            item_total = food.price * quantity
            cart_items.append({
                "food": food,
                "quantity": quantity,
                "item_total": item_total,
            })
            grand_total += item_total

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "grand_total": grand_total,
    })


@login_required
def update_cart(request, food_id):
    if request.method == "POST":
        cart_data = request.session.get("cart", {})
        food_key = str(food_id)
        quantity = request.POST.get("quantity", "1")

        if food_key in cart_data:
            if quantity.isdigit() and 1 <= int(quantity) <= 99:
                cart_data[food_key] = int(quantity)
            else:
                cart_data.pop(food_key, None)

            request.session["cart"] = cart_data
            request.session.modified = True

    return redirect("cart")


@login_required
def checkout(request):
    cart_data = request.session.get("cart", {})
    cart_items = []
    grand_total = 0

    for food_id, quantity in cart_data.items():
        food = Food.objects.filter(
            id=food_id,
            available=True
        ).first()

        if food and isinstance(quantity, int) and quantity > 0:
            item_total = food.price * quantity
            cart_items.append({
                "food": food,
                "quantity": quantity,
                "item_total": item_total,
            })
            grand_total += item_total

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("menu")

    if request.method == "POST":
        address = request.POST.get("delivery_address", "").strip()
        phone = request.POST.get("phone", "").strip()

        if not address or not phone:
            messages.error(request, "Enter your delivery address and phone.")
        elif len(phone) > 15:
            messages.error(request, "Phone number is too long.")
        else:
            for item in cart_items:
                Order.objects.create(
                    customer=request.user,
                    food=item["food"],
                    quantity=item["quantity"],
                    total_price=item["item_total"],
                    delivery_address=address,
                    phone=phone,
                )

            request.session["cart"] = {}
            messages.success(request, "Your order has been placed!")
            return redirect("my_orders")

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "grand_total": grand_total,
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(
        customer=request.user
    ).select_related("food").order_by("-ordered_at")

    return render(request, "my_orders.html", {
        "orders": orders,
    })