// signup.js - Validación corregida con mensajes de alerta

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const checkbox = document.getElementById("agree_terms");
  const submitBtn = form.querySelector("button[type='submit']");

  console.log("Script cargado correctamente"); // Debug

  if (checkbox && submitBtn) {
    // El botón permanece habilitado para permitir la validación
    checkbox.addEventListener("change", function () {
      clearAlerts();
      console.log("Checkbox cambiado:", checkbox.checked); // Debug
    });

    form.addEventListener("submit", function (e) {
      console.log("Formulario enviado"); // Debug
      
      // Siempre prevenir el envío primero para hacer la validación
      e.preventDefault();
      
      clearAlerts();
      let valid = true;

      const firstName = document.getElementById("first_name");
      const lastName = document.getElementById("last_name");
      const email = document.getElementById("email");
      const password = document.getElementById("password");
      const confirm = document.getElementById("confirm_password");

      // Validaciones de campos
      if (!firstName.value.trim()) {
        showAlert(firstName, "* Campo obligatorio");
        valid = false;
      }
      
      if (!lastName.value.trim()) {
        showAlert(lastName, "* Campo obligatorio");
        valid = false;
      }
      
      if (!email.value.trim()) {
        showAlert(email, "* Email obligatorio");
        valid = false;
      } else if (!isValidEmail(email.value)) {
        showAlert(email, "* Formato de email inválido");
        valid = false;
      }

      if (!password.value.trim()) {
        showAlert(password, "* Contraseña obligatoria");
        valid = false;
      } else if (password.value.length < 8 || !/[A-Z]/.test(password.value) || !/[0-9]/.test(password.value)) {
        showAlert(password, "* Mín. 8 caracteres, una mayúscula y un número");
        valid = false;
      }

      if (!confirm.value.trim()) {
        showAlert(confirm, "* Confirmar contraseña es obligatorio");
        valid = false;
      } else if (confirm.value !== password.value) {
        showAlert(confirm, "* Las contraseñas no coinciden");
        valid = false;
      }

      // Validación específica para términos y condiciones
      if (!checkbox.checked) {
        console.log("Términos no aceptados"); // Debug
        showTermsAlert();
        valid = false;
      }

      console.log("Formulario válido:", valid); // Debug

      // Si todo es válido, enviar el formulario
      if (valid) {
        console.log("Enviando formulario..."); // Debug
        // Remover el event listener temporalmente para evitar bucle
        form.removeEventListener("submit", arguments.callee);
        form.submit();
      } else {
        // Hacer scroll al primer error
        setTimeout(() => {
          const firstError = document.querySelector(".error-message");
          if (firstError) {
            firstError.scrollIntoView({ behavior: "smooth", block: "center" });
          }
        }, 100);
      }
    });
  }

  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  function showAlert(input, msg) {
    // Verificar si ya existe un mensaje de error para este campo
    const existingError = input.parentNode.querySelector(".error-message");
    if (existingError) {
      existingError.remove();
    }

    const div = document.createElement("div");
    div.className = "error-message field-error";
    div.style.cssText = `
      color: #ff4444;
      font-size: 12px;
      margin-top: 5px;
      font-weight: 500;
      display: block;
    `;
    div.innerText = msg;
    input.parentNode.appendChild(div);
    console.log("Mensaje de error agregado:", msg); // Debug
  }

  function showTermsAlert() {
    // Remover mensaje anterior si existe
    const existingTermsError = document.querySelector(".terms-error");
    if (existingTermsError) {
      existingTermsError.remove();
    }

    const termsContainer = document.querySelector(".terms-privacy");
    if (!termsContainer) {
      console.log("No se encontró el contenedor de términos"); // Debug
      return;
    }

    // Crear mensaje de error específico para términos y condiciones
    const error = document.createElement("div");
    error.className = "error-message terms-error";
    error.style.cssText = `
      color: #ff4444;
      font-size: 14px;
      margin: 10px 0;
      font-weight: 500;
      padding: 12px;
      background-color: rgba(255, 68, 68, 0.1);
      border: 1px solid #ff4444;
      border-radius: 6px;
      display: block;
      text-align: center;
    `;
    error.innerHTML = "⚠️ Debes aceptar los Términos de Servicio y la Política de Privacidad para crear tu cuenta";
    
    // Insertar el mensaje después del contenedor de términos
    termsContainer.parentNode.insertBefore(error, termsContainer.nextSibling);
    
    // Agregar efecto visual al checkbox
    termsContainer.style.cssText = `
      border: 2px solid #ff4444 !important;
      border-radius: 6px !important;
      padding: 10px !important;
      background-color: rgba(255, 68, 68, 0.05) !important;
      margin: 10px 0 !important;
    `;
    
    console.log("Mensaje de términos agregado"); // Debug
    
    // Remover el efecto visual después de 5 segundos
    setTimeout(() => {
      if (termsContainer) {
        termsContainer.style.cssText = "";
      }
    }, 5000);
  }

  function clearAlerts() {
    // Remover todos los mensajes de error
    const errorMessages = document.querySelectorAll(".error-message");
    errorMessages.forEach(e => {
      e.remove();
      console.log("Mensaje de error removido"); // Debug
    });
    
    // Limpiar estilos del contenedor de términos
    const termsContainer = document.querySelector(".terms-privacy");
    if (termsContainer) {
      termsContainer.style.cssText = "";
    }
  }

  function setupModal(triggerId, modalId, url) {
    const trigger = document.getElementById(triggerId);
    const modal = document.getElementById(modalId);
    
    if (!trigger || !modal) {
      console.log("Modal elements not found:", triggerId, modalId); // Debug
      return;
    }

    const close = modal.querySelector(".close");
    const body = modal.querySelector(".modal-body");

    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      modal.style.display = "flex";
      
      if (body) {
        body.innerHTML = "Cargando...";
        fetch(url)
          .then(res => res.text())
          .then(html => {
            body.innerHTML = html;
          })
          .catch(err => {
            console.error("Error loading modal content:", err);
            body.innerHTML = "Error al cargar el contenido";
          });
      }
    });

    if (close) {
      close.addEventListener("click", function () {
        modal.style.display = "none";
      });
    }

    window.addEventListener("click", function (e) {
      if (e.target === modal) {
        modal.style.display = "none";
      }
    });
  }

  // Configurar modales
  setupModal("openTerms", "modalTerms", "/static/accounts/legal/terms_of_service.html");
  setupModal("openPrivacy", "modalPrivacy", "/static/accounts/legal/privacy_policy.html");
  setupModal("openTermsFooter", "modalTerms", "/static/accounts/legal/terms_of_service.html");
  setupModal("openPrivacyFooter", "modalPrivacy", "/static/accounts/legal/privacy_policy.html");
});