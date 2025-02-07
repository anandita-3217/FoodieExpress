from decimal import Decimal
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Q
from .models import User, Restaurant, MenuItem, Order, OrderItem, DeliveryPartner
from .forms import (RegistrationForm, MenuItemForm)
from django.views.decorators.http import require_http_methods


# AUTH VIEWS
def index(request):
    return render(request,"core/index.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        return render(request, "core/login.html", {
            "message": "Invalid username and/or password."
        })
    return render(request, "core/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        return render(request, "core/register.html", {"form": form})
    return render(request, "core/register.html", {"form": RegistrationForm()})

# CUSTOMER VIEWS
@login_required
def restaurant_list(request):
    query = request.GET.get('q', '')
    restaurants = Restaurant.objects.filter(
        Q(name__icontains=query) |
        Q(cuisine__icontains=query),
        is_active=True
    )
    return render(request, "core/restaurant_list.html", {"restaurants": restaurants})

@login_required
def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    menu_items = restaurant.menu_items.filter(availability='available')
    if request.GET.get('veg_only'):
        menu_items = menu_items.filter(is_vegetarian=True)
    return render(request, "core/restaurant_detail.html", {
        "restaurant": restaurant,
        "menu_items": menu_items
    })


@login_required
def customer_profile(request):
    return render(request,'core/customer_profile.html')

@login_required
@require_POST
def customer_profile_update(request):
    try:

        data = json.loads(request.body)
        user = request.user
        if user.user_type == 'customer':
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.email = data.get('email', user.email)
            user.phone_number = data.get('phone_number', user.phone_number)
            user.address = data.get('address', user.address)
            user.save()
            return JsonResponse({
                'status': 'success',
                'data': {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'address': user.address
                }
            })
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    veg_only = request.GET.get('veg_only', False)
    menu_items = []
    restaurants = []

    if query:
        menu_items = MenuItem.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            availability='available'
        )
        if veg_only:
            menu_items = menu_items.filter(is_vegetarian=True)

        restaurants = Restaurant.objects.filter(
            Q(name__icontains=query) |
            Q(cuisine__icontains=query),
            is_active=True
        )
    
    return render(request, "core/search.html", {
        "menu_items": menu_items,
        "restaurants": restaurants,
        "query": query
    })



@login_required
def customer_order_history(request): 
    orders = Order.objects.filter(customer=request.user).order_by('-created_at').prefetch_related('order_items__menu_item')
    return render(request, "core/customer_order_history.html", {"orders": orders})

@login_required
def order_tracking(request, order_id=None):
    try:
        if order_id:
            
            order = get_object_or_404(Order, id=order_id)
            
           
            if request.user.user_type == 'customer' and order.customer != request.user:
                return HttpResponseForbidden("Not authorized to view this order")
            elif request.user.user_type == 'restaurant' and order.restaurant.owner != request.user:
                return HttpResponseForbidden("Not authorized to view this order")
            elif request.user.user_type == 'delivery_partner' and (not order.delivery_partner or order.delivery_partner.user != request.user):
                return HttpResponseForbidden("Not authorized to view this order")
        else:
            
            if request.user.user_type == 'customer':
                order = Order.objects.filter(
                    customer=request.user,
                    status__in=['received', 'active', 'picked_up']
                ).latest('created_at')
            elif request.user.user_type == 'restaurant':
                order = Order.objects.filter(
                    restaurant__owner=request.user,
                    status__in=['received', 'active', 'picked_up']
                ).latest('created_at')
            elif request.user.user_type == 'delivery_partner':
                delivery_partner = DeliveryPartner.objects.get(user=request.user)
                order = Order.objects.filter(
                    delivery_partner=delivery_partner,
                    status__in=['active', 'picked_up']
                ).latest('created_at')
                
        return render(request, 'core/order_tracking.html', {'order': order})
        
    except (Order.DoesNotExist, DeliveryPartner.DoesNotExist):
        return render(request, 'core/order_tracking.html', {'order': None})

@login_required
@require_http_methods(["POST"])
def update_order_status(request, order_id):
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        order = get_object_or_404(Order, id=order_id)
        
        
        if request.user.user_type == 'restaurant' and order.restaurant.owner == request.user:
            if new_status == 'active' and order.status == 'received':
                
                order.status = 'active'
                order.save()
                
                
                if order.assign_delivery_partner():
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Order status updated and delivery partner assigned'
                    })
                else:
                   
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Order status updated but no delivery partner available'
                    })
                    
            elif new_status == 'picked_up' and order.status == 'active':
                order.status = 'picked_up'
                order.save()
                return JsonResponse({'status': 'success'})
                
        
        elif request.user.user_type == 'delivery_partner':
            if order.delivery_partner and order.delivery_partner.user == request.user:
                if order.status == 'picked_up' and new_status == 'delivered':
                    if order.complete_delivery():
                        return JsonResponse({'status': 'success'})
                        
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid status update request'
        }, status=400)
            
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def get_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    
    if request.user.user_type == 'customer' and order.customer != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    elif request.user.user_type == 'restaurant' and order.restaurant.owner != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)
        
    return JsonResponse({
        'status': order.status,
        'delivery_partner': order.delivery_partner.user.username if order.delivery_partner else None
    })

@require_POST
@login_required
def add_to_cart(request):
    menu_item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        menu_item = MenuItem.objects.get(id=menu_item_id)
        if 'cart' not in request.session:
            request.session['cart'] = {}
            
        cart = request.session['cart']
        if menu_item_id in cart:
            cart[menu_item_id]['quantity'] += quantity
        else:
            cart[menu_item_id] = {
                'quantity': quantity,
                'name': menu_item.name,
                'price': str(menu_item.price),
                'restaurant_id': menu_item.restaurant.id
            }
            
        request.session.modified = True

        total_items = sum(item['quantity'] for item in cart.values())
        total_amount = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
        
        return JsonResponse({
            'status': 'success',
            'message': f'{menu_item.name} added to cart',
            'cart_total': str(total_amount),
            'item_count': total_items
        })
        
    except MenuItem.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Menu item not found'
        }, status=404)

@login_required
def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if not cart:
            return JsonResponse({'status': 'error', 'message': 'Cart is empty'})
            
        try:
            first_item_id = next(iter(cart))
            first_item = MenuItem.objects.get(id=first_item_id)
            restaurant = first_item.restaurant
            order = Order.objects.create(
                customer=request.user,
                restaurant=restaurant,
                status='received',
                total_amount=sum(Decimal(item['price']) * item['quantity'] for item in cart.values()),
                delivery_address=request.user.address
            )
            
            for item_id, item_data in cart.items():
                menu_item = MenuItem.objects.get(id=item_id)
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=item_data['quantity'],
                    subtotal=Decimal(item_data['price']) * item_data['quantity']
                ) 

            del request.session['cart']
            
            return JsonResponse({
                'status': 'success',
                'message': 'Order placed successfully',
                'order_id': order.id
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    
    cart_total = sum(
        Decimal(item['price']) * item['quantity'] 
        for item in cart.values()
    )
    delivery_fee = max(cart_total * Decimal('0.05'), Decimal('50.00'))
    total_with_delivery = cart_total + delivery_fee
    
    return render(request, 'core/cart.html', {
        'cart_total': cart_total,
        'delivery_fee': delivery_fee,
        'total_with_delivery': total_with_delivery
    })

@require_POST
@login_required
def remove_item(request):
    item_id = request.POST.get('item_id')
    cart = request.session.get('cart', {})
    
    if item_id in cart:
        del cart[item_id]
        request.session.modified = True
        
        return JsonResponse({
            'status': 'success',
            'message': 'Item removed from cart'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Item not found in cart'
    })

@require_POST
@login_required
def update_quantity(request):
    item_id = request.POST.get('item_id')
    action = request.POST.get('action')
    cart = request.session.get('cart', {})
    
    if item_id in cart:
        if action == 'increase':
            cart[item_id]['quantity'] += 1
        elif action == 'decrease':
            if cart[item_id]['quantity'] > 1:
                cart[item_id]['quantity'] -= 1
            else:
                del cart[item_id]
                
        request.session.modified = True
        
        return JsonResponse({
            'status': 'success',
            'message': 'Quantity updated'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Item not found in cart'
    })

###########################################################################################
# RESTAURANT VIEWS.

@login_required
def restaurant_profile(request):
    if request.user.user_type != 'restaurant':
        return redirect('home')
    restaurant = Restaurant.objects.get(owner=request.user)
    return render(request, 'core/restaurant_profile.html', {'restaurant': restaurant})

@login_required
@require_POST
def restaurant_profile_update(request):
    if request.user.user_type != 'restaurant':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        restaurant = Restaurant.objects.get(owner=request.user)
        if 'name' in data and data['name'].strip():  
            restaurant.name = data['name']
            
        if 'description' in data and data['description'].strip():
            restaurant.description = data['description']
            
        if 'cuisine' in data and data['cuisine'].strip():
            restaurant.cuisine = data['cuisine']
            
        if 'is_pure_veg' in data:
            restaurant.is_pure_veg = data['is_pure_veg'] == 'true'
            
        if 'photo' in data and data['photo'].strip():  
            restaurant.photo = data['photo']
            
        restaurant.save()
        user = request.user
        if 'email' in data and data['email'].strip():  
            user.email = data['email']
            
        if 'phone_number' in data and data['phone_number'].strip():
            user.phone_number = data['phone_number']
            
        if 'address' in data and data['address'].strip():
            user.address = data['address']
            
        user.save()
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'name': restaurant.name,
                'description': restaurant.description,
                'cuisine': restaurant.cuisine,
                'is_pure_veg': restaurant.is_pure_veg,
                'photo': restaurant.photo,
                'email': user.email,
                'phone_number': user.phone_number,
                'address': user.address
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
@login_required
def restaurant_menu(request):
    if request.user.user_type != 'restaurant':
        return redirect('home')
    
    restaurant = Restaurant.objects.get(owner=request.user)
    menu_items = MenuItem.objects.filter(restaurant=restaurant)
    return render(request, 'core/restaurant_menu.html', {
        'menu_items': menu_items
    })

@login_required
def menu_search(request):
    if request.user.user_type != 'restaurant':
        return redirect('home')
    
    query = request.GET.get('q', '').strip()
    if not query:
        return redirect('restaurant_menu')
    
    restaurant = Restaurant.objects.get(owner=request.user)
    menu_items = MenuItem.objects.filter(
        restaurant=restaurant,
        name__icontains=query
    )
    
    if len(menu_items) == 1:
       
        return redirect(f'/restaurant/menu/#menuItem-{menu_items[0].id}')
    
    return render(request, 'core/restaurant_menu.html', {
        'menu_items': menu_items,
        'search_query': query
    })

@login_required
@require_POST
def update_menu_item_status(request, item_id):
    if request.user.user_type != 'restaurant':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        menu_item = MenuItem.objects.get(
            id=item_id,
            restaurant__owner=request.user
        )
        menu_item.availability = data['status']
        menu_item.save()
        return JsonResponse({'status': 'success'})
    except (MenuItem.DoesNotExist, KeyError):
        return JsonResponse({'status': 'error'}, status=400)

@login_required
@require_http_methods(['DELETE'])
def delete_menu_item(request, item_id):
    if request.user.user_type != 'restaurant':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    try:
        menu_item = MenuItem.objects.get(
            id=item_id,
            restaurant__owner=request.user
        )
        menu_item.delete()
        return JsonResponse({'status': 'success'})
    except MenuItem.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=400)

@login_required
def edit_menu_item(request, item_id):
    if request.user.user_type != 'restaurant':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    try:
        menu_item = MenuItem.objects.get(
            id=item_id,
            restaurant__owner=request.user
        )
        
        if request.method == 'GET':
            data = {
                'name': menu_item.name,
                'description': menu_item.description,
                'price': str(menu_item.price),
                'is_vegetarian': menu_item.is_vegetarian,
                'is_bestseller': menu_item.is_bestseller,
                'availability': menu_item.availability,
                'photo_url': menu_item.photo_url or ''
            }
            return JsonResponse({'status': 'success', 'data': data})
            
        elif request.method == 'PUT':
            data = json.loads(request.body)
            
            menu_item.name = data.get('name')
            menu_item.description = data.get('description')
            menu_item.price = data.get('price')
            menu_item.is_vegetarian = data.get('is_vegetarian')
            menu_item.is_bestseller = data.get('is_bestseller')
            menu_item.availability = data.get('availability')
            menu_item.photo_url = data.get('photo_url')
            
            menu_item.save()
            return JsonResponse({'status': 'success'})
            
    except MenuItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)
    except (ValueError, KeyError) as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    

@login_required
def restaurant_order_history(request):
    if request.user.user_type != User.RESTAURANT:
        return HttpResponseForbidden("You are not authorized to view this page.")
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
    except Restaurant.DoesNotExist:
        return render(request, "core/restaurant_history.html", {"orders": [], "message": "No associated restaurant found."})

    orders = Order.objects.filter(restaurant=restaurant).order_by('-created_at').prefetch_related('order_items__menu_item')
    return render(request, "core/restaurant_history.html", {"orders": orders})

@login_required
def restaurant_dashboard(request):
    if request.user.user_type != User.RESTAURANT:
        return redirect('index')
    restaurant = request.user.restaurant
    context = {
        "restaurant": restaurant,
        "menu_items": restaurant.menu_items.all(),
        "orders": Order.objects.filter(restaurant=restaurant).order_by('-created_at'),
        "active_orders": Order.objects.filter(
            restaurant=restaurant,
            status__in=['active', 'ready', 'picked_up']
        )
    }
    return render(request, "core/restaurant_dashboard.html", context)

@login_required
def menu_item_add(request):
    if request.user.user_type != User.RESTAURANT:
        return redirect('index')
    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.restaurant = request.user.restaurant
            menu_item.save()
            return redirect('restaurant_dashboard')
    return render(request, "core/menu_item_form.html", {"form": MenuItemForm()})

###########################################################################################

# DELIVERY PARTNER VIEWS

@login_required
def delivery_profile(request):
    return render(request,'core/delivery_profile.html')
@login_required
@require_POST
def delivery_profile_update(request):
    try:
        data = json.loads(request.body)
        user = request.user
        if user.user_type == 'delivery_partner':
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.email = data.get('email', user.email)
            user.phone_number = data.get('phone_number', user.phone_number)
            user.address = data.get('address', user.address)
            user.save()
            return JsonResponse({
                'status': 'success',
                'data': {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'address': user.address
                }
            })
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def delivery_partner_dashboard(request):
    if request.user.user_type != 'delivery_partner':
        return redirect('home')
        
    delivery_partner = DeliveryPartner.objects.get(user=request.user)
    context = {
        'current_restaurant': delivery_partner.restaurant,
        'total_deliveries': delivery_partner.total_deliveries,
        'total_earnings': delivery_partner.total_earnings,
        'is_available': delivery_partner.is_available  
    }
    return render(request, 'core/delivery_dashboard.html', context)

@login_required
def delivery_partner_registration_page(request):
    
    if request.user.user_type != 'delivery_partner':
        return redirect('home')
    
    delivery_partner = DeliveryPartner.objects.get(user=request.user)
    context = {
        'current_restaurant': delivery_partner.restaurant
    }
    return render(request, 'core/delivery_partner_register.html', context)

@login_required
@require_http_methods(["GET"])
def get_available_restaurants(request):
    
    if request.user.user_type != 'delivery_partner':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        restaurants = Restaurant.objects.filter(is_active=True)
        available_restaurants = []
        
        for restaurant in restaurants:
            if restaurant.can_accept_partner():
                available_restaurants.append({
                    'id': restaurant.id,
                    'name': restaurant.name,
                    'address': restaurant.owner.address,
                    'description': restaurant.description,
                    'cuisine': restaurant.cuisine,
                    'current_partners': restaurant.current_partner_count,
                    'max_partners': restaurant.max_delivery_partners
                })
        
        return JsonResponse({
            'success': True,
            'restaurants': available_restaurants
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def register_with_restaurant(request):
    if request.user.user_type != 'delivery_partner':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        
        data = json.loads(request.body)
        restaurant_id = data.get('restaurant_id')
        
        if not restaurant_id:
            return JsonResponse({
                'success': False,
                'error': 'Restaurant ID is required'
            }, status=400)

        delivery_partner = DeliveryPartner.objects.get(user=request.user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
        if delivery_partner.restaurant:
            return JsonResponse({
                'success': False,
                'error': 'Already registered with a restaurant'
            }, status=400)
            
        if restaurant.can_accept_partner():
            delivery_partner.restaurant = restaurant
            delivery_partner.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully registered with {restaurant.name}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Restaurant cannot accept more delivery partners'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def unregister_from_restaurant(request):
    if request.user.user_type != 'delivery_partner':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        delivery_partner = DeliveryPartner.objects.get(user=request.user)
        
        if delivery_partner.current_order:
            return JsonResponse({
                'success': False,
                'error': 'Cannot unregister while having an active order'
            }, status=400)
        
        restaurant = delivery_partner.restaurant
        if restaurant:
            restaurant_name = restaurant.name  
            delivery_partner.restaurant = None
            delivery_partner.save()
            return JsonResponse({
                'success': True,
                'message': f'Successfully unregistered from {restaurant_name}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Not registered with any restaurant'
            }, status=400)
            
    except DeliveryPartner.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Delivery partner profile not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def toggle_availability(request):
    if request.user.user_type != 'delivery_partner':
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized access'
        }, status=403)
    
    try:
        delivery_partner = DeliveryPartner.objects.get(user=request.user)
        
        
        if delivery_partner.current_order and delivery_partner.is_available:
            return JsonResponse({
                'success': False,
                'error': 'Cannot go offline while having an active order'
            }, status=400)
        
        
        delivery_partner.is_available = not delivery_partner.is_available
        delivery_partner.save()
        
        
        request.session['delivery_partner_available'] = delivery_partner.is_available
        
        return JsonResponse({
            'success': True,
            'is_available': delivery_partner.is_available,
            'message': f'You are now {"online" if delivery_partner.is_available else "offline"}'
        })
        
    except DeliveryPartner.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Delivery partner profile not found'
        }, status=404)


@login_required
def delivery_orders(request):
    if not hasattr(request.user, 'deliverypartner'):
        return redirect('home')
    
    delivery_partner = request.user.deliverypartner
    completed_orders = delivery_partner.delivery_orders.filter(
        status='delivered'
    ).order_by('-created_at')
    
    return render(request, 'core/delivery_order.html', {
        'delivery_partner': delivery_partner,
        'completed_orders': completed_orders,
    })

@login_required
def check_new_orders(request):
    try:
        if not hasattr(request.user, 'deliverypartner'):
            return JsonResponse({'has_new_orders': False})
            
        delivery_partner = request.user.deliverypartner
        
        
        new_order = Order.objects.filter(
            delivery_partner=delivery_partner,
            status='active'  
        ).order_by('-created_at').first()
        
        if new_order:
            return JsonResponse({
                'has_new_orders': True,
                'order_data': {
                    'id': new_order.id,
                    'restaurant_name': new_order.restaurant.name,
                    'customer_name': new_order.customer.username,
                    'delivery_address': new_order.delivery_address,
                    'total_amount': str(new_order.total_amount)
                }
            })
            
        return JsonResponse({'has_new_orders': False})
        
    except Exception as e:
        return JsonResponse({
            'has_new_orders': False,
            'error': str(e)
        })
    




