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
                
                if (label.textContent.trim() !== 'Username') {
                    const input = document.createElement('input');
                    input.type = label.textContent === 'Email' ? 'email' : 'text';
                    input.className = 'form-control';
                    input.value = text.textContent.trim();
                    input.name = label.textContent.toLowerCase().trim().replace(' ', '_');
                    text.replaceWith(input);
                }
            });

            editButton.innerHTML = '<i class="bi bi-person-check-fill"></i> Save Changes';
            editButton.classList.replace('btn-outline-primary', 'btn-primary');
            isEditing = true;
        }

        async function saveChanges() {
            const formData = {};
            profileData.querySelectorAll('input').forEach(input => {
                if (input.name) {
                    formData[input.name] = input.value.trim();
                }
            });

            try {
                const response = await fetch('/profile/update/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                if (data.status === 'success') {
                    showMessage('Profile updated successfully!', 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showMessage(data.message || 'Error updating profile');
                }
            } catch (error) {
                showMessage('Error connecting to server. Please try again.');
            }
        }
    }
});