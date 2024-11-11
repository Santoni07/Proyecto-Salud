from django import forms
from .models import *

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

class ElectroBasalForm(forms.ModelForm):
    class Meta:
        model = ElectroBasal
        fields = [
            'ritmo', 'PQ', 'frecuencia', 'arritmias', 'ejeQRS', 
            'trazadoNormal', 'observaciones'
        ]
        widgets = {
            'ritmo': forms.TextInput(attrs={'class': 'form-control'}),
            'PQ': forms.TextInput(attrs={'class': 'form-control'}),
            'frecuencia': forms.TextInput(attrs={'class': 'form-control'}),
            'arritmias': forms.TextInput(attrs={'class': 'form-control'}),
            'ejeQRS': forms.TextInput(attrs={'class': 'form-control'}),
            'trazadoNormal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ElectroEsfuerzoForm(forms.ModelForm):
    class Meta:
        model = ElectroEsfuerzo
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CardiovascularForm(forms.ModelForm):
    class Meta:
        model = Cardiovascular
        fields = [
            'auscultacion', 'soplos', 'R1', 'tension_arterial', 'R2', 
            'observaciones', 'ruidos_agregados'
        ]
        widgets = {
            'auscultacion': forms.TextInput(attrs={'class': 'form-control'}),
            'soplos': forms.TextInput(attrs={'class': 'form-control'}),
            'R1': forms.TextInput(attrs={'class': 'form-control'}),
            'tension_arterial': forms.TextInput(attrs={'class': 'form-control'}),
            'R2': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ruidos_agregados': forms.TextInput(attrs={'class': 'form-control'}),
        }


class LaboratorioForm(forms.ModelForm):
    class Meta:
        model = Laboratorio
        fields = [
            'citologico', 'orina', 'colesterol', 'uremia', 'glucemia', 
            'otros' 
        ]
        widgets = {
            'citologico': forms.TextInput(attrs={'class': 'form-control'}),
            'orina': forms.TextInput(attrs={'class': 'form-control'}),
            'colesterol': forms.TextInput(attrs={'class': 'form-control'}),
            'uremia': forms.TextInput(attrs={'class': 'form-control'}),
            'glucemia': forms.TextInput(attrs={'class': 'form-control'}),
            'otros': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ToraxForm(forms.ModelForm):
    class Meta:
        model = Torax
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class OftalmologicoForm(forms.ModelForm):
    class Meta:
        model = Oftalmologico
        fields = ['od', 'oi']
        widgets = {
            'od': forms.TextInput(attrs={'class': 'form-control'}),
            'oi': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RegistroMedicoUpdateForm(forms.ModelForm):
    class Meta:
        model = RegistroMedico
        fields = ['estado', 'observacion', 'fecha_creacion', 'fecha_caducidad']
        widgets = {
            'fecha_creacion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_caducidad': forms.DateInput(attrs={'type': 'date'}),
        }