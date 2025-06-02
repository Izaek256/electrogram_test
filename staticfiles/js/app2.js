/**
 * Button Loader Management System
 * 
 * This script provides centralized functionality for managing button loaders
 * across all authentication forms (sign up, sign in, profile update, password update).
 */

document.addEventListener('DOMContentLoaded', function() {
    // Configure AlertifyJS if it exists
    if (typeof alertify !== 'undefined') {
        alertify.set('notifier', 'position', 'top-right');
        alertify.set('notifier', 'delay', 5);
    }

    // Get CSRF token from cookie
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

    /**
     * Initialize button loaders for a form
     * @param {string} formId - The ID of the form
     * @param {string} buttonId - The ID of the button
     * @param {boolean} useAjax - Whether to use AJAX for form submission
     * @param {function} successCallback - Callback function on successful AJAX submission
     */
    function initButtonLoader(formId, buttonId, useAjax = false, successCallback = null) {
        const form = document.getElementById(formId);
        const button = document.getElementById(buttonId);
        
        if (!form || !button) return;
        
        const btnText = button.querySelector('.btn-text');
        const btnLoader = button.querySelector('.btn-loader');
        
        // Initialize loader style
        if (btnLoader) btnLoader.style.display = 'none';
        
        form.addEventListener('submit', function(e) {
            // Show loader and hide text
            if (btnText) btnText.style.display = 'none';
            if (btnLoader) btnLoader.style.display = 'inline-block';
            
            // If not using AJAX, let the form submit normally
            if (!useAjax) return;
            
            // For AJAX submissions
            e.preventDefault();
            
            // Clear previous alerts if alertify exists
            if (typeof alertify !== 'undefined') {
                alertify.dismissAll();
            }
            
            // Get form data
            const formData = new FormData(form);
            
            // Submit form via AJAX
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    if (typeof alertify !== 'undefined') {
                        alertify.success(data.message || 'Operation completed successfully!');
                    }
                    
                    // Restore button state before any callbacks or redirects
                    if (btnText) btnText.style.display = 'inline-block';
                    if (btnLoader) btnLoader.style.display = 'none';
                    
                    // Call success callback if provided
                    if (successCallback && typeof successCallback === 'function') {
                        successCallback(data);
                    }
                    
                    // Redirect if URL is provided
                    if (data.redirect_url) {
                        setTimeout(() => {
                            window.location.href = data.redirect_url;
                        }, 1000);
                    }
                } else {
                    // Handle errors
                    if (data.errors) {
                        Object.values(data.errors).forEach(error => {
                            if (Array.isArray(error)) {
                                error.forEach(err => {
                                    if (typeof alertify !== 'undefined') alertify.error(err);
                                });
                            } else {
                                if (typeof alertify !== 'undefined') alertify.error(error);
                            }
                        });
                    } else if (data.message) {
                        if (typeof alertify !== 'undefined') alertify.error(data.message);
                    }
                    
                    // Restore button state
                    if (btnText) btnText.style.display = 'inline-block';
                    if (btnLoader) btnLoader.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (typeof alertify !== 'undefined') {
                    alertify.error('An error occurred. Please try again.');
                }
                
                // Restore button state
                if (btnText) btnText.style.display = 'inline-block';
                if (btnLoader) btnLoader.style.display = 'none';
            });
        });
    }

    // Initialize button loaders for each form
    // Sign Up Form (standard form submission, no AJAX)
    initButtonLoader('signup-form', 'register-btn', false);
    
    // Sign In Form (AJAX submission)
    initButtonLoader('signin-form', 'signin-btn', true);
    
    // Profile Update Form (AJAX submission with custom success callback)
    initButtonLoader('profile-form', 'update-profile-btn', true, function(data) {
        // Update the displayed username
        const usernameElement = document.querySelector('.dash__text h2');
        if (usernameElement && data.user_data) {
            usernameElement.textContent = data.user_data.username;
        }

        // Update form fields with new data
        if (data.user_data) {
            const fields = ['username', 'email', 'first_name', 'last_name'];
            fields.forEach(field => {
                const input = document.querySelector(`[name="${field}"]`);
                if (input && data.user_data[field]) {
                    input.value = data.user_data[field];
                }
            });
        }
    });
    
    // Password Update Form (AJAX submission)
    initButtonLoader('password-form', 'update-password-btn', true);
});
