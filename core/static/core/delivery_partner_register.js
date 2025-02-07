document.addEventListener('DOMContentLoaded', function() {
    loadRestaurants();
});

function loadRestaurants() {
    const loadingDiv = document.getElementById('loading');
    const restaurantList = document.getElementById('restaurantList');
    
    fetch('/api/restaurants/available/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            loadingDiv.style.display = 'none';
            
            if (!data.success) {
                showAlert(data.error || 'Error loading restaurants', 'error');
                return;
            }
            
            if (data.restaurants.length === 0) {
                restaurantList.innerHTML = `
                    <div class="alert alert-accent text-center">
                        No restaurants are currently accepting delivery partners.
                    </div>
                `;
                return;
            }
            
            const currentRestaurantId = document.getElementById('restaurantList').dataset.currentRestaurant;
            
            restaurantList.innerHTML = data.restaurants.map(restaurant => {
                const isRegistered = currentRestaurantId && parseInt(currentRestaurantId) === restaurant.id;
                const buttonText = isRegistered ? 'Unregister' : 'Register';
                const buttonClass = isRegistered ? 'btn-outline-danger' : 'btn-accent';
                
                return `
                    <div class="restaurant-card p-4">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h5 class="mb-2">${restaurant.name}</h5>
                                <p class="mb-2">${restaurant.address}</p>
                                <p class="text-muted mb-2">${restaurant.cuisine}</p>
                                <p class="mb-2">${restaurant.description}</p>
                                <div class="capacity-badge available">
                                    Partners: ${restaurant.current_partners} / ${restaurant.max_partners}
                                </div>
                            </div>
                            <button 
                                data-restaurant-id="${restaurant.id}"
                                data-action="${isRegistered ? 'unregister' : 'register'}"
                                class="btn ${buttonClass} restaurant-action-btn"
                                ${!isRegistered && restaurant.current_partners >= restaurant.max_partners ? 'disabled' : ''}
                            >
                                ${buttonText}
                            </button>
                        </div>
                    </div>
                `;
            }).join('');

            
            addButtonEventListeners();
        })
        .catch(error => {
            loadingDiv.style.display = 'none';
            showAlert('Error loading restaurants: ' + error.message, 'error');
            console.error('Error:', error);
        });
}

function addButtonEventListeners() {
    document.querySelectorAll('.restaurant-action-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const restaurantId = this.dataset.restaurantId;
            const action = this.dataset.action;
            
            if (action === 'register') {
                registerWithRestaurant(restaurantId, this);
            } else {
                unregisterFromRestaurant(restaurantId, this);
            }
        });
    });
}

function registerWithRestaurant(restaurantId, buttonElement) {
    
    const originalText = buttonElement.textContent;
    buttonElement.disabled = true;
    buttonElement.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Registering...
    `;
    
    fetch('/api/restaurants/register/', {
        method: 'POST',
        body: JSON.stringify({ restaurant_id: restaurantId }),
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 500) {
                throw new Error('Server error. Please try again later.');
            }
            return response.json().then(data => {
                throw new Error(data.error || 'Registration failed');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            setTimeout(() => {
                window.location.href = '/delivery-partner/dashboard/';
            }, 1500);
        } else {
            throw new Error(data.error || 'Registration failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert(error.message, 'error');
        buttonElement.disabled = false;
        buttonElement.textContent = originalText;
    });
}

function unregisterFromRestaurant(restaurantId, buttonElement) {
    if (!confirm('Are you sure you want to unregister from this restaurant?')) {
        return;
    }

    const originalText = buttonElement.textContent;
    buttonElement.disabled = true;
    buttonElement.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Unregistering...
    `;
    
    fetch('/api/restaurants/unregister/', {
        method: 'POST',
        body: JSON.stringify({ restaurant_id: restaurantId }),
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 500) {
                throw new Error('Server error. Please try again later.');
            }
            return response.json().then(data => {
                throw new Error(data.error || 'Unregistration failed');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            throw new Error(data.error || 'Unregistration failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert(error.message, 'error');
        buttonElement.disabled = false;
        buttonElement.textContent = originalText;
    });
}

function showAlert(message, type) {
    const alert = document.getElementById('alert');
    alert.className = `alert ${type === 'success' ? 'alert-accent' : 'alert-danger'} mt-4`;
    alert.textContent = message;
    alert.classList.remove('d-none');
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}