from django.contrib import admin
from django.utils.html import format_html
from .models import AntecedenteEnfermedades, EstudiosMedico, RegistroMedico

# Registro de AntecedenteEnfermedades en el admin
@admin.register(AntecedenteEnfermedades)
class AntecedenteEnfermedadesAdmin(admin.ModelAdmin):
    list_display = ('idantecedente_enfermedades', 'get_jugador', 'fue_operado', 'toma_medicacion', 'es_diabetico', 'es_amatico')
    search_fields = ('idantecedente_enfermedades',)
    list_filter = ('fue_operado', 'toma_medicacion', 'es_diabetico', 'es_amatico')

    def get_jugador(self, obj):
        # Accede al jugador a través de la ficha médica
        return f"{obj.idfichaMedica.jugador.persona.profile.nombre} {obj.idfichaMedica.jugador.persona.profile.apellido}"
    
    get_jugador.short_description = 'Jugador'


# Registro de RegistroMedico en el admin
@admin.register(RegistroMedico)
class RegistroMedicoAdmin(admin.ModelAdmin):
    list_display = ('idfichaMedica', 'jugador', 'torneo', 'estado', 'fecha_creacion', 'fecha_caducidad')
    search_fields = ('idfichaMedica', 'jugador__nombre', 'torneo__nombre')
    list_filter = ('estado', 'torneo', 'fecha_creacion')
    # Agrega más filtros o campos de búsqueda según tu necesidad

@admin.register(EstudiosMedico)
class EstudioMedicoAdmin(admin.ModelAdmin):
    list_display = ['ficha_medica', 'tipo_estudio', 'archivo_link']
    search_fields = ['ficha_medica__jugador__nombre', 'ficha_medica__jugador__apellido', 'tipo_estudio']
    list_filter = ['tipo_estudio']

    def archivo_link(self, obj):
        if obj.archivo:
            return format_html('<a href="{}" target="_blank">Ver Archivo</a>', obj.archivo.url)
        return "No disponible"
    archivo_link.short_description = 'Archivo'

   