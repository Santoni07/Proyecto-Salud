from django import forms
from .models import  RegistroMedico, AntecedenteEnfermedades,EstudiosMedico

class RegistroMedicoForm(forms.ModelForm):
    class Meta:
        model = RegistroMedico
        fields = [
            'jugador',
            'torneo',
            'estado',
            'fecha_caducidad',
            'observacion',
            'consentimiento_persona',
        ]
        widgets = {
            'fecha_caducidad': forms.SelectDateWidget(),  # Widget para selección de fecha
            'observacion': forms.Textarea(attrs={'rows': 4, 'cols': 40}),  # Textarea para observaciones
        }

class AntecedenteEnfermedadesForm(forms.ModelForm):
    class Meta:
        model = AntecedenteEnfermedades
        fields = [
            'fue_operado',
            'toma_medicacion',
            'estuvo_internado',
            'sufre_hormigueos',
            'es_diabetico',
            'es_amatico',
            'es_alergico',
            'alerg_observ',
            'antecedente_epilepsia',
            'desviacion_columna',
            'dolor_cintira',
            'fracturas',
            'dolores_articulares',
            'falta_aire',
            'tramatismos_craneo',
            'dolor_pecho',
            'perdida_conocimiento',
            'presion_arterial',
            'muerte_subita_familiar',
            'enfermedad_cardiaca_familiar',
            'soplo_cardiaco',
            'abstenerce_competencia',
            'antecedentes_coronarios_familiares',
            'fumar_hipertension_diabetes',
            'fhd_observacion',
            'consumo_cocaina_anabolicos',
            'cca_observaciones',
            
        ]
        widgets = {
            'alerg_observ': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'fhd_observacion': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
            'cca_observaciones': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
        }

class EstudioMedicoForm(forms.ModelForm):
    class Meta:
        model = EstudiosMedico
        fields = ['tipo_estudio', 'observaciones', 'archivo']  # Elimina el espacio adicional en 'observaciones'
        
        # Definimos los widgets para personalizar la apariencia de los campos en el formulario
        widgets = {
            'tipo_estudio': forms.Select(attrs={'class': 'form-control'}),  
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),  
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),  
        } 