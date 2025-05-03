document.addEventListener('DOMContentLoaded', function() {
   
    const loginForm = document.querySelector('form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            let hasError = false;
            
            
            const existingErrors = document.querySelectorAll('.error-message');
            existingErrors.forEach(error => error.remove());
            
            if (!email) {
                createErrorMessage('Please enter your email address');
                hasError = true;
            } else if (!isValidEmail(email)) {
                createErrorMessage('Please enter a valid email address');
                hasError = true;
            }
            
            if (!password) {
                createErrorMessage('Please enter your password');
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