document.addEventListener('DOMContentLoaded', function() {
    
    const deliveryPartnerId = JSON.parse(document.getElementById('delivery_partner_id').textContent);
    const ws_scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const orderSocket = new WebSocket(
        `${ws_scheme}://${window.location.host}/ws/delivery_partner/${deliveryPartnerId}/`
    );

    
    orderSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'new_order') {
            showOrderAlert(data.order);
            updateCurrentOrder(data.order);
        }
    };

    function showOrderAlert(order) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-accent alert-dismissible fade show';
        alertDiv.innerHTML = `
            <strong>New Order Assignment!</strong>
            <p>Order #${order.id} from ${order.restaurant_name}</p>
            <p>Delivery to: ${order.delivery_address}</p>
            <p>Amount: ₹${order.total_amount}</p>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        


        const alertsContainer = document.getElementById('orderAlerts');
        alertsContainer.appendChild(alertDiv);


        setTimeout(() => {
            if (alertDiv && document.body.contains(alertDiv)) {
                alertDiv.remove();
            }
        }, 10000);
    }

    function updateCurrentOrder(order) {
        const currentOrderCard = document.getElementById('currentOrderCard');
        const currentOrderDetails = document.getElementById('currentOrderDetails');
        
        currentOrderCard.style.display = 'block';
        currentOrderDetails.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Order #${order.id}</h6>
                    <p><strong>Restaurant:</strong> ${order.restaurant_name}</p>
                    <p><strong>Customer:</strong> ${order.customer_name}</p>
                    <p><strong>Amount:</strong> ₹${order.total_amount}</p>
                </div>
                <div class="col-md-6">
                    <h6>Delivery Details</h6>
                    <p><strong>Address:</strong> ${order.delivery_address}</p>
                    <p><strong>Phone:</strong> ${order.customer_phone}</p>
                    <div class="mt-3">
                        <button class="btn btn-accent" onclick="updateOrderStatus(${order.id}, 'picked_up')">
                            Mark as Picked Up
                        </button>
                        <button class="btn btn-success ms-2" onclick="updateOrderStatus(${order.id}, 'delivered')">
                            Mark as Delivered
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    
    window.updateOrderStatus = async function(orderId, status) {
        try {
            const response = await fetch('/delivery/update_order_status/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    order_id: orderId,
                    status: status
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                if (status === 'delivered') {
                    document.getElementById('currentOrderCard').style.display = 'none';
                    location.reload(); 
                }
                showMessage(`Order successfully marked as ${status}`, 'success');
            } else {
                showMessage(data.message || 'Error updating order status');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('Error connecting to server. Please try again.');
        }
    };

    function showMessage(message, type = 'warning') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'success' ? 'accent' : 'danger'} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const alertsContainer = document.getElementById('orderAlerts');
        alertsContainer.appendChild(alert);

        setTimeout(() => {
            if (alert && document.body.contains(alert)) {
                alert.remove();
            }
        }, 5000);
    }
});