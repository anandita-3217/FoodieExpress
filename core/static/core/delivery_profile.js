document.addEventListener('DOMContentLoaded', function() {
    
    const editButton = document.getElementById('editButton');
    const profileData = document.getElementById('profileData');
    const container = document.querySelector('.container-fluid');


    function showMessage(message, type = 'warning') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
        alert.role = 'alert';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        
        const existingAlert = container.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        container.insertBefore(alert, container.firstChild);

        
        setTimeout(() => {
            if (alert && document.body.contains(alert)) {
                alert.remove();
            }
        }, 5000);
    }

    
    if (editButton && profileData) {
        let isEditing = false;

        editButton.addEventListener('click', (e) => {
            e.preventDefault();
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
                
                
                const fieldName = label.textContent.trim().toLowerCase();
                if (fieldName === 'username') return;

                
                const input = document.createElement('input');
                input.type = fieldName === 'email' ? 'email' : 
                            fieldName === 'phone number' ? 'tel' : 'text';
                input.className = 'form-control';
                input.value = text.textContent.trim();
                input.name = fieldName.replace(' ', '_');
                
                
                if (fieldName === 'phone number') {
                    input.pattern = "[0-9]{10,15}";
                    input.title = "Phone number must be between 10 and 15 digits";
                }
                
                
                text.replaceWith(input);
            });

            
            editButton.innerHTML = '<i class="bi bi-person-check"></i> Save Changes';
            editButton.classList.add('active');
            isEditing = true;
        }

        async function saveChanges() {

            const formData = {};
            const inputs = profileData.querySelectorAll('input');
            let isValid = true;

            inputs.forEach(input => {
                if (input.name) {
                    
                    if (!input.value.trim()) {
                        showMessage(`${input.name.replace('_', ' ')} cannot be empty`);
                        isValid = false;
                        return;
                    }
                    
                    
                    if (input.name === 'phone_number' && !input.checkValidity()) {
                        showMessage('Please enter a valid phone number (10-15 digits)');
                        isValid = false;
                        return;
                    }

                    
                    if (input.name === 'email' && !input.checkValidity()) {
                        showMessage('Please enter a valid email address');
                        isValid = false;
                        return;
                    }

                    formData[input.name] = input.value.trim();
                }
            });

            if (!isValid) return;

            try {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                const response = await fetch('/delivery_profile/update/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(formData)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.status === 'success') {
                    showMessage('Profile updated successfully!', 'success');
                    setTimeout(() => location.reload(), 1500);
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