
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}


function updateProgressBar(status) {
    const progressSteps = {
        'received': 1,
        'active': 2,
        'picked_up': 3,
        'delivered': 4
    };
    
    const progressItems = document.querySelectorAll('.progressbar li');
    const currentStep = progressSteps[status] || 0;
    
    progressItems.forEach((item, index) => {
        if (index < currentStep) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}


function updateStatusBadge(status) {
    const badge = document.querySelector('.badge');
    if (badge) {
        badge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        
        const badgeClass = status === 'delivered' ? 'success' : 'warning';
        badge.className = `badge bg-${badgeClass}`;
    }
}


function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const cardBody = document.querySelector('.card-body');
    cardBody.insertBefore(alertDiv, cardBody.firstChild);
    
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}


async function updateOrderStatus(orderId, newStatus) {
    try {
        console.log('Sending update:', {
            orderId,
            newStatus,
            csrf: getCsrfToken()
        });

        const response = await fetch(`/orders/${orderId}/update-status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ status: newStatus })
        });

        console.log('Response status:', response.status);
        
        const responseText = await response.text();
        console.log('Response text:', responseText);

        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}: ${responseText}`);
        }

        let data;
        try {
            data = JSON.parse(responseText);
        } catch (e) {
            throw new Error('Invalid JSON response from server');
        }

        if (data.status === 'success') {

            updateProgressBar(newStatus);
            updateStatusBadge(newStatus);
            
            
            showAlert(data.message || 'Order status updated successfully', 'success');
            
            
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            throw new Error(data.message || 'Failed to update order status');
        }
    } catch (error) {
        console.error('Detailed error:', error);
        showAlert('Failed to update order status: ' + error.message, 'danger');
    }
}


async function checkDeliveryPartnerAssignment(orderId) {
    try {
        const response = await fetch(`/orders/${orderId}/status/`);
        if (!response.ok) {
            throw new Error('Failed to fetch order status');
        }
        
        const data = await response.json();
        
        if (data.delivery_partner) {
            
            showAlert('Delivery partner assigned! Refreshing page...', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        }
    } catch (error) {
        console.error('Error checking delivery partner:', error);
    }
}


async function checkNewOrders() {
    try {
        const response = await fetch('/check-new-orders/');
        const data = await response.json();
        
        if (data.has_new_orders) {
            showAlert('New orders available! Refreshing page...', 'info');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        }
    } catch (error) {
        console.error('Error checking new orders:', error);
    }
}


function attachEventListeners() {
    document.querySelectorAll('.update-status').forEach(button => {
        button.addEventListener('click', function() {
            const orderId = this.dataset.orderId;
            const newStatus = this.dataset.status;
            
            
            this.disabled = true;
            
            updateOrderStatus(orderId, newStatus);
        });
    });
}


document.addEventListener('DOMContentLoaded', function() {
    
    attachEventListeners();
    
    
    const orderStatus = document.querySelector('.badge')?.textContent.toLowerCase();
    const hasDeliveryPartner = document.querySelector('[data-delivery-partner]');
    const orderId = document.querySelector('[data-order-id]')?.dataset.orderId;
    const userType = document.querySelector('meta[name="user-type"]')?.content;
    
    
    if (orderId) {
        if (orderStatus === 'active' && !hasDeliveryPartner) {
            
            setInterval(() => checkDeliveryPartnerAssignment(orderId), 10000);
        }
        
        if (userType === 'restaurant' || userType === 'delivery_partner') {
            
            setInterval(checkNewOrders, 30000);
        }
    }
});