from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone # Necesario para default=timezone.now si lo usas

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.message[:20]}"
    

class Consulta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    consulta = models.TextField()
    resultado = models.TextField(null=True, blank=True)  # Aquí se guarda la respuesta automática
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.consulta


class FormularioFinanzas(models.Model):
    # Manteniendo unique=True de la versión anterior, es una buena práctica si cada usuario solo debe tener un formulario.
    # Si quieres permitir múltiples formularios por usuario, quita unique=True y ajusta tu lógica en views.py.
    usuario_id = models.CharField(max_length=255, unique=True) # Longitud actualizada y manteniendo unique=True
    nombre = models.CharField(max_length=100)
    ingresos_mensuales = models.DecimalField(max_digits=10, decimal_places=2) # CAMBIADO a DecimalField
    gasto_alimentacion = models.DecimalField(max_digits=10, decimal_places=2)  # CAMBIADO a DecimalField
    gasto_transporte = models.DecimalField(max_digits=10, decimal_places=2)    # CAMBIADO a DecimalField
    gasto_entretenimiento = models.DecimalField(max_digits=10, decimal_places=2) # CAMBIADO a DecimalField
    gasto_hogar = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # CAMBIADO a DecimalField, default ajustado
    meta_ahorro = models.DecimalField(max_digits=10, decimal_places=2)           # CAMBIADO a DecimalField
    ahorro_mensual = models.DecimalField(max_digits=10, decimal_places=2)        # CAMBIADO a DecimalField
    recomendaciones = models.TextField()
    
    # El campo 'timestamp' de tu versión anterior ha sido reemplazado por 'fecha_actualizacion'
    # Si necesitas ambos (creación y actualización), puedes tener los dos:
    # timestamp_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateField(auto_now=True) # Campo añadido y configurado para auto-actualización

    def __str__(self): # Corregido el nombre del método a __str__
        return self.nombre # Cambiado para que devuelva solo el nombre, como en tu nueva definición


class RegistroFinanciero(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    total_gastos = models.DecimalField(max_digits=12, decimal_places=2)
    ahorro_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    meta_ahorro = models.DecimalField(max_digits=12, decimal_places=2)

class GastoCategoria(models.Model):
    registro = models.ForeignKey(RegistroFinanciero, related_name='categorias', on_delete=models.CASCADE)
    categoria = models.CharField(max_length=100)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)