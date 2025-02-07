from django.urls import path

from . import views

urlpatterns = [
    # AUTH PATHS

    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    # CUSTOMER PATHS
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurant/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('profile/update/', views.customer_profile_update, name='customer_profile_update'),
    path('customer_order_history/', views.customer_order_history, name='customer_order_history'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove-item/', views.remove_item, name='remove_item'),
    path('cart/update-quantity/', views.update_quantity, name='update_quantity'),
    path('search/', views.search, name='search'),

    # ORDERS
    path('orders/latest/', views.order_tracking, name='latest_order_tracking'),
    path('orders/<int:order_id>/', views.order_tracking, name='order_tracking'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('check-new-orders/', views.check_new_orders, name='check_new_orders'),
    path('orders/<int:order_id>/status/', views.get_order_status, name='get_order_status'),

    # RESTAURANT PATHS
    path('restaurant/profile/', views.restaurant_profile, name='restaurant_profile'),
    path('restaurant/profile/update/', views.restaurant_profile_update, name='restaurant_profile_update'),
    path('restaurant/menu/', views.restaurant_menu, name='restaurant_menu'),
    path('restaurant/menu/search/', views.menu_search, name='menu_search'),
    path('restaurant/menu/update-status/<int:item_id>/', views.update_menu_item_status, name='update_menu_item_status'),
    path('restaurant/menu/delete/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),
    path('restaurant/menu/edit/<int:item_id>/', views.edit_menu_item, name='edit_menu_item'),
    path('restaurant_order_history/', views.restaurant_order_history, name='restaurant_order_history'),
    path('restaurant/menu/add/', views.menu_item_add, name='menu_item_add'),
    path('restaurant/dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
      
    
    # DELIVERY PATHS
    path('delivery_profile/', views.delivery_profile, name='delivery_profile'),
    path('delivery_profile/update/', views.delivery_profile_update, name='delivery_profile_update'),
    path('delivery-partner/dashboard/', views.delivery_partner_dashboard, name='delivery_partner_dashboard'),
    path('delivery-partner/register/', views.delivery_partner_registration_page, name='delivery_partner_registration'),
    path('api/restaurants/available/', views.get_available_restaurants, name='available_restaurants'),
    path('api/restaurants/register/', views.register_with_restaurant, name='register_with_restaurant'),
    path('api/restaurants/unregister/', views.unregister_from_restaurant, name='unregister_from_restaurant'),
    path('api/delivery-partner/toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('delivery/orders/', views.delivery_orders, name='delivery_orders'),
    path('delivery/update_order_status/', views.update_order_status, name='update_order_status'),

   
    


]