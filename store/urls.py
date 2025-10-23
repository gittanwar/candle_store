from django.urls import path
from . import views

urlpatterns = [
    # Home & Product
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Cart URLs
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    # pageproduct
    path('properties/', views.properties_by_location, name='properties_all'),
    path('properties/<int:location_id>/', views.properties_by_location, name='properties_by_location'),

    # subscription
    path('subscribe/', views.subscribe, name='subscribe'),
    # add to cart detail page
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),


]

