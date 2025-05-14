document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const checkbox = document.getElementById("agree_terms");
    const submitBtn = form.querySelector("button[type='submit']");
    const fields = ["first_name", "last_name", "email"];

    // 🔁 Restaurar datos
    fields.forEach(id => {
        const input = document.getElementById(id);
        if (input && localStorage.getItem(id)) {
            input.value = localStorage.getItem(id);
        }
    });

    if (form) {
        form.addEventListener("submit", function (e) {
            const existingErrors = document.querySelectorAll('.error-message');
            existingErrors.forEach(error => error.remove());

            const firstName = document.getElementById('first_name').value.trim();
            const lastName = document.getElementById('last_name').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            const agreeTerms = checkbox.checked;

            let hasError = false;

            if (!firstName) {
                createErrorMessage('Por favor ingresa tu nombre');
                hasError = true;
            }
            if (!lastName) {
                createErrorMessage('Por favor ingresa tu apellido');
                hasError = true;
            }
            if (!email) {
                createErrorMessage('Por favor ingresa tu email');
                hasError = true;
            } else if (!isValidEmail(email)) {
                createErrorMessage('El email no es válido');
                hasError = true;
            }
            if (!password) {
                createErrorMessage('Ingresa una contraseña');
                hasError = true;
            } else if (password.length < 8) {
                createErrorMessage('La contraseña debe tener mínimo 8 caracteres');
                hasError = true;
            }
            if (password !== confirmPassword) {
                createErrorMessage('Las contraseñas no coinciden');
                hasError = true;
            }
            if (!agreeTerms) {
                createErrorMessage('Debes aceptar los Términos y la Política de Privacidad para continuar.');
                hasError = true;
            }

            if (hasError) {
                e.preventDefault();
            } else {
                // 🧹 Limpia localStorage si todo está bien
                fields.forEach(id => localStorage.removeItem(id));
            }
        });

        // 🔁 Limpiar mensaje si se marca el checkbox después
        checkbox.addEventListener("change", function () {
            const msg = document.getElementById("terms-msg");
            if (checkbox.checked && msg) msg.remove();
        });
    }

    function createErrorMessage(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        form.insertBefore(errorDiv, form.firstChild);
    }

    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
});

// 💾 Guardar campos al salir
window.addEventListener("beforeunload", function () {
    const fields = ["first_name", "last_name", "email"];
    fields.forEach(id => {
        const input = document.getElementById(id);
        if (input) localStorage.setItem(id, input.value);
    });
});
