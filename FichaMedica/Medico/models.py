from django.db import models
from .models import Profile, RegistroMedico

class Medico(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="medico")  # Relación uno a uno con Profile
    registro_medico = models.ManyToManyField(RegistroMedico, related_name="medicos")  # Relación muchos a muchos con RegistroMedico
    matricula = models.CharField(max_length=20, unique=True)  # Número de matrícula del médico
    especialidad = models.CharField(max_length=100, blank=True, null=True)  # Especialidad médica
    telefono_consultorio = models.CharField(max_length=15, blank=True, null=True)  # Teléfono del consultorio

    class Meta:
        db_table = 'medico'
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"

    def __str__(self):
        return f"Dr./Dra. {self.profile.nombre} {self.profile.apellido} - {self.especialidad}"
