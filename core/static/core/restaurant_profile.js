document.addEventListener('DOMContentLoaded', function() {
    const editButton = document.getElementById('editButton');
    const profileData = document.getElementById('profileData');
    const container = document.querySelector('.container');

    function showMessage(message, type = 'warning') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.role = 'alert';
        alert.innerHTML = `
            <strong>${type === 'success' ? 'Success!' : 'Error!'}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        container.insertBefore(alert, container.firstChild);
        
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    }

    if (editButton && profileData) {
        let isEditing = false;

        editButton.addEventListener('click', () => {
            if (!isEditing) {
                startEditing();
            } else {
                saveChanges();
            }
        });

        function startEditing() {
            const profileTexts = profileData.querySelectorAll('.profile-text');
            
            profileTexts.forEach(text => {
                const label = text.previousElementSibling;
                if (!label || !label.textContent) return;
                
                if (label.textContent.trim() === 'Pure Vegetarian') {
                    const select = document.createElement('select');
                    select.className = 'form-control';
                    select.name = 'is_pure_veg';
                    select.innerHTML = `
                        <option value="true" ${text.textContent === 'Yes' ? 'selected' : ''}>Yes</option>
                        <option value="false" ${text.textContent === 'No' ? 'selected' : ''}>No</option>
                    `;
                    text.replaceWith(select);
                } else {
                    const input = document.createElement('input');
                    input.type = label.textContent === 'Email' ? 'email' : 'text';
                    input.className = 'form-control';
                    input.value = text.textContent.trim();
                    input.name = label.textContent.toLowerCase().trim().replace(' ', '_');
                    text.replaceWith(input);
                }
            });

            editButton.innerHTML = '<i class="bi bi-check-circle"></i> Save Changes';
            editButton.classList.add('btn-success');
            isEditing = true;
        }

        async function saveChanges() {
            const formData = {};
            profileData.querySelectorAll('input, select').forEach(input => {
                if (input.name) {

                    const fieldName = input.name.toLowerCase()
                        .replace('restaurant_name', 'name')
                        .replace('photo_url', 'photo')
                        .replace('owner_email', 'email');
                    formData[fieldName] = input.value.trim();
                }
            });
        
            try {
                const response = await fetch('/restaurant/profile/update/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify(formData)
                });
        
                const data = await response.json();
                if (data.status === 'success') {
                    showMessage('Restaurant profile updated successfully!', 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showMessage(data.message || 'Error updating profile');
                }
            } catch (error) {
                console.error('Error:', error);
                showMessage('Error connecting to server. Please try again.');
            }
        }
    }
});