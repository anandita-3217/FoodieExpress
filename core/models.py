
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.timezone import now

def validate_phone_number(value):
    if not value.isdigit() or len(value) < 10 or len(value) > 15:
        raise ValidationError('Phone number must be numeric and between 10 to 15 digits.')

class User(AbstractUser):
    CUSTOMER = 'customer'
    RESTAURANT = 'restaurant'
    DELIVERY_PARTNER = 'delivery_partner'
    
    USER_TYPE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (RESTAURANT, 'Restaurant'),
        (DELIVERY_PARTNER, 'Delivery Partner'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.user_type}"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_type']),
            models.Index(fields=['phone_number'])
        ]

class Restaurant(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    cuisine = models.CharField(max_length=50)
    is_pure_veg = models.BooleanField(default=False)
    photo = models.URLField(max_length=1000, blank=True, null=True)
    min_delivery_partners = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    max_delivery_partners = models.IntegerField(default=10, validators=[MaxValueValidator(10)])
    is_active = models.BooleanField(default=True)

    @property
    def current_partner_count(self):
        return self.delivery_partners.count()
    
    def can_accept_partner(self):
        return self.current_partner_count < self.max_delivery_partners

    def __str__(self):
        return f"{self.name} - Owner: {self.owner.username}"

    class Meta:
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['cuisine'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'owner'],
                name='unique_restaurant_owner'
            )
        ]

class MenuItem(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('removed', 'Removed')
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_vegetarian = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available')
    photo_url = models.URLField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name} (₹{self.price})"

    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        ordering = ['restaurant', 'name']
        unique_together = ['restaurant', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_vegetarian']),
            models.Index(fields=['availability'])
        ]

class DeliveryPartner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deliveries = models.PositiveIntegerField(default=0)
    current_order = models.OneToOneField('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_delivery')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_partners')

    def register_with_restaurant(self, restaurant):
        if restaurant.can_accept_partner():
            self.restaurant = restaurant
            self.save()
            return True
        return False

    def is_available_for_order(self):
        return self.is_available and self.current_order is None and self.restaurant is not None
    
    def update_earnings(self, order):
        earning_amount = order.total_amount * 0.05 
        self.total_earnings += earning_amount
        self.total_deliveries += 1
        self.save()
    
    def __str__(self):
        return f"Delivery Partner: {self.user.username} - Deliveries: {self.total_deliveries}"

    class Meta:
        verbose_name = 'Delivery Partner'
        verbose_name_plural = 'Delivery Partners'
        ordering = ['-total_deliveries']
        indexes = [
            models.Index(fields=['is_available']),
            models.Index(fields=['total_deliveries'])
        ]

class Order(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('active', 'Active'),
        ('picked_up', 'Picked Up'),
        ('delivered', 'Delivered'),
        ('inactive', 'Inactive'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='restaurant_orders')
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.SET_NULL, null=True, related_name='delivery_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def assign_delivery_partner(self):
        available_partner = DeliveryPartner.objects.filter(
            is_available=True,
            restaurant=self.restaurant,
            current_order__isnull=True
        ).order_by('id').first()
        
        if available_partner:
            self.delivery_partner = available_partner
            self.status = 'active'
            self.save()
            
            available_partner.current_order = self
            available_partner.save()
            return True
        return False

    def complete_delivery(self):
        if self.delivery_partner and self.status == 'picked_up':
            self.status = 'delivered'
            
            from decimal import Decimal
            min_earnings = Decimal('50.00')
            percentage_earnings = self.total_amount * Decimal('0.05')
            earning_amount = max(min_earnings, percentage_earnings)
            
            
            if self.delivery_partner:
                self.delivery_partner.total_earnings += earning_amount
                self.delivery_partner.total_deliveries += 1
                self.delivery_partner.current_order = None
                self.delivery_partner.save()
            
            self.save()
            return True
        return False


    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} from {self.restaurant.name}"

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['customer', 'status'])
        ]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.menu_item.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} in Order #{self.order.id}"

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['order', 'menu_item']
        unique_together = ['order', 'menu_item']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['menu_item'])
        ]