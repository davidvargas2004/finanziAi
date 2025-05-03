document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.querySelector('form');
    
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            // Remove any existing error messages
            const existingErrors = document.querySelectorAll('.error-message');
            existingErrors.forEach(error => error.remove());
            
            // Get form values
            const firstName = document.getElementById('first_name').value.trim();
            const lastName = document.getElementById('last_name').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            const agreeTerms = document.getElementById('agree_terms').checked;
            
            let hasError = false;
            
            // Validate first name
            if (!firstName) {
                createErrorMessage('Please enter your first name');
                hasError = true;
            }
            
            // Validate last name
            if (!lastName) {
                createErrorMessage('Please enter your last name');
                hasError = true;
            }
            
            // Validate email
            if (!email) {
                createErrorMessage('Please enter your email address');
                hasError = true;
            } else if (!isValidEmail(email)) {
                createErrorMessage('Please enter a valid email address');
                hasError = true;
            }
            
            // Validate password
            if (!password) {
                createErrorMessage('Please enter a password');
                hasError = true;
            } else if (password.length < 8) {
                createErrorMessage('Password must be at least 8 characters long');
                hasError = true;
            }
            
            // Validate password confirmation
            if (password !== confirmPassword) {
                createErrorMessage('Passwords do not match');
                hasError = true;
            }
            
            // Validate terms agreement
            if (!agreeTerms) {
                createErrorMessage('You must agree to the Terms of Service and Privacy Policy');
                hasError = true;
            }
            
            if (hasError) {
                e.preventDefault();
            }
        });
    }
    
    function createErrorMessage(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        const form = document.querySelector('form');
        form.insertBefore(errorDiv, form.firstChild);
    }
    
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
});