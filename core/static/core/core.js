// Registration
document.addEventListener('DOMContentLoaded', function() {
    const userTypeRadios = document.querySelectorAll('.user-type-radio input');
    if (userTypeRadios.length > 0) {
        const registrationFields = document.getElementById('registration-fields');
        const restaurantFields = document.getElementById('restaurant-fields');
        
        const addFieldProperties = () => {
            const fields = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea');
            fields.forEach(field => {
                field.classList.add('form-control');
                if (!field.placeholder) {
                    const fieldName = field.name.replace(/_/g, ' ').replace(/(\w)(\w*)/g, 
                        (g0,g1,g2) => g1.toUpperCase() + g2);
                    field.placeholder = fieldName;
                }
            });
        };

        userTypeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                registrationFields.style.display = 'block';
                
                if (this.value === 'restaurant') {
                    restaurantFields.style.display = 'block';
                    document.querySelectorAll('#restaurant-fields input[type="text"], #restaurant-fields textarea')
                        .forEach(field => field.required = true);
                } else {
                    restaurantFields.style.display = 'none';
                    document.querySelectorAll('#restaurant-fields input[type="text"], #restaurant-fields textarea')
                        .forEach(field => field.required = false);
                }
                
                addFieldProperties();
            });
        });
        addFieldProperties();
    }

    // All restaurants
    const vegOnlyCheckbox = document.getElementById('vegOnly');
    if (vegOnlyCheckbox) {
        vegOnlyCheckbox.addEventListener('change', function() {
            const currentUrl = new URL(window.location.href);
            if (this.checked) {
                currentUrl.searchParams.set('veg_only', 'true');
            } else {
                currentUrl.searchParams.delete('veg_only');
            }
            window.location.href = currentUrl.toString();
        });
    }
// Cart
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            
            fetch('/add-to-cart/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `item_id=${itemId}&quantity=1`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    
                    showNotification(data.message, 'success');
                    
                    
                    updateCartCount(data.item_count);
                    

                    updateCartTotal(data.cart_total);
                } else {
                    showNotification(data.message, 'error');
                }
            })
            .catch(error => {
                showNotification('Error adding item to cart', 'error');
                console.error('Error:', error);
            });
        });
    });
    
    // Helper functions
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed`;
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '1000';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    function updateCartCount(count) {
        const cartCount = document.querySelector('.cart-count');
        if (cartCount) {
            cartCount.textContent = count;
        }
    }
    
    function updateCartTotal(total) {
        const cartTotal = document.querySelector('.cart-total');
        if (cartTotal) {
            cartTotal.textContent = `₹${total}`;
        }
    }


        // Remove item from cart
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch('/cart/remove-item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `item_id=${itemId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.reload();
                } else {
                    alert('Error removing item from cart');
                }
            });
        });
    });

    // Update quantity
    document.querySelectorAll('.update-quantity').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            const action = this.dataset.action;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch('/cart/update-quantity/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `item_id=${itemId}&action=${action}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.reload();
                } else {
                    alert('Error updating quantity');
                }
            });
        });
    });

    // Checkout button
    document.getElementById('checkout-button')?.addEventListener('click', function() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/cart/checkout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = `/orders/${data.order_id}/`;
            } else {
                alert(data.message || 'Error processing checkout');
            }
        });
    });
    
    

});