
let isAvailable = false;

document.addEventListener("DOMContentLoaded", function () {

    const availabilityBtn = document.getElementById('availabilityBtn');
    isAvailable = availabilityBtn.dataset.available === 'true';
    updateAvailabilityUI();



    const ordersContainer = document.getElementById("orders-container");
    const checkboxes = document.querySelectorAll(".btn-check");
    

    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
            const selectedFilters = Array.from(checkboxes)
                .filter((box) => box.checked)
                .map((box) => box.id.replace("filter-", ""));
            
            filterOrders(selectedFilters);
        });
    });
});

function filterOrders(selectedFilters) {
    const orders = document.querySelectorAll(".order-card");
    orders.forEach((order) => {
        const orderStatus = order.getAttribute("data-status");
        if (selectedFilters.length === 0 || selectedFilters.includes(orderStatus)) {
            order.style.display = "block";
        } else {
            order.style.display = "none";
        }
    });
}

function toggleAvailability() {
    const button = document.getElementById('availabilityBtn');
    const statusAlert = document.getElementById('statusAlert');

    
    
    const originalText = button.textContent;
    button.disabled = true;
    button.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Updating...
    `;

   
    fetch('/api/delivery-partner/toggle-availability/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            isAvailable = data.is_available;
            updateAvailabilityUI();
            showStatus(data.message || 'Availability updated successfully', 'success');

        } else {
            showStatus(data.error || 'Failed to update availability', 'error');
            
            updateAvailabilityUI();

        }
    })
    .catch(error => {
        showStatus('Error updating availability', 'error');
        console.error('Error:', error);
        
        updateAvailabilityUI();

    })
    .finally(() => {
        
        button.disabled = false;
        updateAvailabilityUI();
    });
}

function updateAvailabilityUI() {
    const button = document.getElementById('availabilityBtn');
    if (button) {
        button.textContent = isAvailable ? 'Go Offline' : 'Go Online';
        button.className = `btn ${isAvailable ? 'btn-success' : 'btn-accent'}`;
       
        button.dataset.available = isAvailable.toString();
    }
}

function showStatus(message, type) {
    const statusAlert = document.getElementById('statusAlert');
    if (statusAlert) {
        statusAlert.className = `alert ${type === 'success' ? 'alert-accent' : 'alert-danger'} mt-3`;
        statusAlert.textContent = message;
        statusAlert.classList.remove('d-none');

       
        setTimeout(() => {
            statusAlert.classList.add('d-none');
        }, 3000);
    }
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

function refreshOrders() {
    fetch('/api/delivery-partner/orders/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateOrdersUI(data.orders);
            } else {
                showStatus('Failed to refresh orders', 'error');
            }
        })
        .catch(error => {
            showStatus('Error refreshing orders', 'error');
            console.error('Error:', error);
        });
}

function updateOrdersUI(orders) {
    const ordersContainer = document.getElementById('orders-container');
    if (!ordersContainer) return;

    if (orders.length === 0) {
        ordersContainer.innerHTML = `
            <div class="alert alert-accent text-center">
                No orders available.
            </div>
        `;
        return;
    }

    ordersContainer.innerHTML = orders.map(order => `
        <div class="card shadow-sm mb-3 order-card" data-status="${order.status.toLowerCase()}">
            <div class="card-body">
                <p><strong>Order Id:</strong> ${order.id}</p>
                <p><strong>Status:</strong> ${order.status_display}</p>
                <p><strong>Total Amount:</strong> ₹${order.total_amount}</p>
                <p><strong>Created At:</strong> ${order.created_at}</p>
            </div>
        </div>
    `).join('');

    
    const selectedFilters = Array.from(document.querySelectorAll('.btn-check:checked'))
        .map(checkbox => checkbox.id.replace('filter-', ''));
    filterOrders(selectedFilters);
}