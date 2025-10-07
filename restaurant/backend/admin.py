from django.contrib import admin
from .models import (
    Category, MenuItem, Cart, CartItem, Order,
    OrderItem, Payment, Review, Address, Profile
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'available']
    list_filter = ['category', 'available']
    search_fields = ['name', 'description']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__username']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'menu_item', 'quantity']
    search_fields = ['cart__user__username', 'menu_item__name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'total_price', 'placed_at']
    list_filter = ['status']
    search_fields = ['user__username']
    date_hierarchy = 'placed_at'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_item', 'quantity']
    search_fields = ['order__user__username', 'menu_item__name']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'paid', 'payment_date']
    list_filter = ['paid']
    search_fields = ['order__user__username']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'menu_item', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['user__username', 'menu_item__name']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'line1', 'city', 'state', 'pincode']
    search_fields = ['user__username', 'city', 'state', 'pincode']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'phone']
    search_fields = ['user__username', 'name', 'phone']
    