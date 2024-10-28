import os
from django.db import models
from persona.models import  Torneo ,Jugador
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save


class AntecedenteEnfermedades(models.Model):
    
    idantecedente_enfermedades = models.AutoField(primary_key=True)
    fue_operado = models.BooleanField(null=True, blank=True, default=None)
    toma_medicacion = models.BooleanField(null=True, blank=True, default=None)
    estuvo_internado = models.BooleanField(null=True, blank=True, default=None)
    sufre_hormigueos = models.BooleanField(null=True, blank=True, default=None)
    es_diabetico = models.BooleanField(null=True, blank=True, default=None)
    es_amatico = models.BooleanField(null=True, blank=True, default=None)  # 'asmático' corregido como 'es_amatico'
    es_alergico = models.BooleanField(null=True, blank=True, default=None)
    alerg_observ = models.CharField(max_length=100, null=True, blank=True, default=None)
    antecedente_epilepsia = models.BooleanField(null=True, blank=True, default=None)
    desviacion_columna = models.BooleanField(null=True, blank=True, default=None)
    dolor_cintira = models.BooleanField(null=True, blank=True, default=None)
    fracturas = models.BooleanField(null=True, blank=True, default=None)
    dolores_articulares = models.BooleanField(null=True, blank=True, default=None)
    falta_aire = models.BooleanField(null=True, blank=True, default=None)
    tramatismos_craneo = models.BooleanField(null=True, blank=True, default=None)
    dolor_pecho = models.BooleanField(null=True, blank=True, default=None)
    perdida_conocimiento = models.BooleanField(null=True, blank=True, default=None)
    presion_arterial = models.BooleanField(null=True, blank=True, default=None)
    muerte_subita_familiar = models.BooleanField(null=True, blank=True, default=None)
    enfermedad_cardiaca_familiar = models.BooleanField(null=True, blank=True, default=None)
    soplo_cardiaco = models.BooleanField(null=True, blank=True, default=None)
    abstenerce_competencia = models.BooleanField(null=True, blank=True, default=None)
    antecedentes_coronarios_familiares = models.BooleanField(null=True, blank=True, default=None)
    fumar_hipertension_diabetes = models.BooleanField(null=True, blank=True, default=None)
    fhd_observacion = models.CharField(max_length=100, null=True, blank=True, default=None)
    consumo_cocaina_anabolicos = models.BooleanField(null=True, blank=True, default=None)
    cca_observaciones = models.CharField(max_length=100, null=True, blank=True, default=None)

    # Relación con la tabla 'fichamedica'
    idfichaMedica = models.OneToOneField('RegistroMedico', on_delete=models.CASCADE, unique=True)

    class Meta:
        db_table = 'antecedente_enfermedades'


class RegistroMedico(models.Model):
    ESTADO_FICHA = [
    ('PENDIENTE', 'Pendiente'),
    ('PROCESO', 'En proceso'),
    ('APROBADA', 'Aprobada'),
    
    ('RECHAZADA', 'Rechazada'),
    ]
    
    idfichaMedica = models.AutoField(primary_key=True)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)  # Relación con Torneo
    estado = models.CharField(max_length=45, choices=ESTADO_FICHA, blank=True, null=True)  # Estado actual de la ficha médica
    fecha_creacion = models.DateTimeField(auto_now_add=True) 
    fecha_caducidad = models.DateField()  # Fecha de caducidad
    observacion = models.CharField(max_length=200, blank=True, null=True)  # Observaciones adicionales
    consentimiento_persona = models.BooleanField(null=True, blank=True)  # Consentimiento de la persona
    
    class Meta:
        db_table = 'fichaRegistro'

    def __str__(self):
        # Accediendo al nombre y apellido del perfil del jugador
        return f"{self.jugador.persona.profile.nombre} {self.jugador.persona.profile.apellido} "

class EstudiosMedico(models.Model):
    TIPO_ESTUDIO = [
        ('ORINA', 'Análisis de Orina'),
        ('ELECTRO', 'Electrocardiograma'),
        ('ERGOMETRIA', 'Ergometría'),
    ]
    
    idestudio = models.AutoField(primary_key=True)
    ficha_medica = models.ForeignKey(RegistroMedico, on_delete=models.CASCADE)  # Relación con la ficha médica
    tipo_estudio = models.CharField(max_length=20, choices=TIPO_ESTUDIO)  # Tipo de estudio médico
    
    archivo = models.FileField(upload_to='estudios/', null=True, blank=True)  # Archivo cargado (imágenes, PDFs, etc.)
    observaciones = models.CharField(max_length=200, null=True, blank=True)  # Observaciones adicionales
    
    class Meta:
        db_table = 'estudios_medicos'
        verbose_name = 'Estudio Médico'
        verbose_name_plural = 'Estudios Médicos'

    def __str__(self):
        return f'{self.get_tipo_estudio_display()} - {self.ficha_medica.jugador.persona.profile.nombre} {self.ficha_medica.jugador.persona.profile.apellido}'

    # Señal para eliminar el archivo al eliminar el objeto
@receiver(post_delete, sender=EstudiosMedico)
def eliminar_archivo_post_delete(sender, instance, **kwargs):
    if instance.archivo:
        if os.path.isfile(instance.archivo.path):
            os.remove(instance.archivo.path)
