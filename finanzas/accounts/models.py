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

    from django.db import models
from django.contrib.auth.models import User

class Consulta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    consulta = models.TextField()
    resultado = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.consulta[:30]}"

