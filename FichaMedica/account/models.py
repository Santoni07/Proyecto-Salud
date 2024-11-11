from django.conf import settings

from django.db import models




class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=30, blank=True, null=True)
    apellido = models.CharField(max_length=30, blank=True, null=True)
    dni = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True)
    rol = models.CharField(
        max_length=20,
        choices=[
            ('jugador', 'Jugador'),  # Valor predeterminado actualizado a "jugador"
            ('medico', 'Médico'),
            ('representante', 'Representante'),
        ],
        default='jugador'
    )

    class Meta:
        ordering = ['user__username']

    @property
    def edad(self):
        from datetime import date
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return None
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.rol}"