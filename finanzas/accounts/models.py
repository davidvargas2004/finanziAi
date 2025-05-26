from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.message[:20]}"
    

    #Consulta 


class Consulta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    consulta = models.TextField()
    resultado = models.TextField(null=True, blank=True)  # Aquí se guarda la respuesta automática
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.consulta


class FormularioFinanzas(models.Model):
    usuario_id = models.CharField(max_length=50)
    nombre = models.CharField(max_length=100)
    ingresos_mensuales = models.FloatField()
    gasto_alimentacion = models.FloatField()
    gasto_transporte = models.FloatField()
    gasto_entretenimiento = models.FloatField()
    meta_ahorro = models.FloatField()
    ahorro_mensual = models.FloatField()
    recomendaciones = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.timestamp}"
    

  

class RegistroFinanciero(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    total_gastos = models.DecimalField(max_digits=12, decimal_places=2)
    ahorro_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    meta_ahorro = models.DecimalField(max_digits=12, decimal_places=2)

class GastoCategoria(models.Model):
    registro = models.ForeignKey(RegistroFinanciero, related_name='categorias', on_delete=models.CASCADE)
    categoria = models.CharField(max_length=100)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)

