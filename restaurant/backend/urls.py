from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
# from .views import login_view, register_view, logout_view
app_name = 'restaurant'  # For namespacing

urlpatterns = [
    path('',views.home, name='home'),
    path('menu/', views.menu, name='menu'),  # Home page shows categories and items
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/place', views.place_order, name='place-order'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    # path('add-review/<int:menu_item_id>/', views.add_review, name='add_review'),
    path('add-address/', views.manage_address, name='manage_address'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit-profile'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
