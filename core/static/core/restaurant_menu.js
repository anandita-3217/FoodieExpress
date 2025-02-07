document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const availabilitySelects = document.querySelectorAll('.availability-select');
    const deleteButtons = document.querySelectorAll('.delete-item');
    const editButtons = document.querySelectorAll('.edit-item');
    let currentEditItemId = null;
    const editModal = new bootstrap.Modal(document.getElementById('editModal'));

    
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = document.getElementById('searchInput').value.trim();
        window.location.href = `/restaurant/menu/search/?q=${encodeURIComponent(query)}`;
    });


    availabilitySelects.forEach(select => {
        select.addEventListener('change', async function() {
            const itemId = this.dataset.itemId;
            const newStatus = this.value;

            try {
                const response = await fetch(`/restaurant/menu/update-status/${itemId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({ status: newStatus })
                });

                const data = await response.json();
                if (data.status === 'success') {
                    showAlert('Status updated successfully', 'success');
                } else {
                    showAlert('Error updating status', 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                showAlert('Error connecting to server', 'danger');
            }
        });
    });

   
    deleteButtons.forEach(button => {
        button.addEventListener('click', async function() {
            if (confirm('Are you sure you want to delete this item?')) {
                const itemId = this.dataset.itemId;
                try {
                    const response = await fetch(`/restaurant/menu/delete/${itemId}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    });

                    const data = await response.json();
                    if (data.status === 'success') {
                        document.getElementById(`menuItem-${itemId}`).remove();
                        showAlert('Item deleted successfully', 'success');
                    } else {
                        showAlert('Error deleting item', 'danger');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    showAlert('Error connecting to server', 'danger');
                }
            }
        });
    });

 
    editButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const itemId = this.dataset.itemId;
            currentEditItemId = itemId;
            
            try {
                const response = await fetch(`/restaurant/menu/edit/${itemId}/`, {
                    headers: {
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                const data = await response.json();
                
                if (data.status === 'success') {
                    
                    document.getElementById('editName').value = data.data.name;
                    document.getElementById('editDescription').value = data.data.description;
                    document.getElementById('editPrice').value = data.data.price;
                    document.getElementById('editPhotoUrl').value = data.data.photo_url;
                    document.getElementById('editAvailability').value = data.data.availability;
                    document.getElementById('editIsVegetarian').checked = data.data.is_vegetarian;
                    document.getElementById('editIsBestseller').checked = data.data.is_bestseller;
                    
                    editModal.show();
                } else {
                    showAlert('Error loading menu item data', 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                showAlert('Error connecting to server', 'danger');
            }
        });
    });

    
    document.getElementById('saveChanges').addEventListener('click', async function() {
        const updatedData = {
            name: document.getElementById('editName').value,
            description: document.getElementById('editDescription').value,
            price: document.getElementById('editPrice').value,
            photo_url: document.getElementById('editPhotoUrl').value,
            availability: document.getElementById('editAvailability').value,
            is_vegetarian: document.getElementById('editIsVegetarian').checked,
            is_bestseller: document.getElementById('editIsBestseller').checked
        };
        
        try {
            const response = await fetch(`/restaurant/menu/edit/${currentEditItemId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(updatedData)
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                
                const card = document.querySelector(`#menuItem-${currentEditItemId}`);
                card.querySelector('.card-title').textContent = updatedData.name;
                card.querySelector('.card-text').textContent = updatedData.description;
                card.querySelector('strong').nextSibling.textContent = ` ₹${updatedData.price}`;
                
                if (updatedData.photo_url && card.querySelector('.card-img-top')) {
                    card.querySelector('.card-img-top').src = updatedData.photo_url;
                }
                
                
                const vegBadge = card.querySelector('.badge.bg-success');
                if (updatedData.is_vegetarian && !vegBadge) {
                    card.querySelector('.card-text').insertAdjacentHTML('beforeend', 
                        '<span class="badge bg-success ms-1">Veg</span>');
                } else if (!updatedData.is_vegetarian && vegBadge) {
                    vegBadge.remove();
                }
                
                const bestsellerBadge = card.querySelector('.badge.bg-warning');
                if (updatedData.is_bestseller && !bestsellerBadge) {
                    card.querySelector('.card-text').insertAdjacentHTML('beforeend', 
                        '<span class="badge bg-warning ms-1">Bestseller</span>');
                } else if (!updatedData.is_bestseller && bestsellerBadge) {
                    bestsellerBadge.remove();
                }
                
                editModal.hide();
                showAlert('Menu item updated successfully', 'success');
            } else {
                showAlert('Error updating menu item', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('Error connecting to server', 'danger');
        }
    });

    
    function showAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.querySelector('.container').insertBefore(alert, document.querySelector('.row'));
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 3000);
    }
});