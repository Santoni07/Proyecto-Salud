
from urllib import request
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.db.models import Q, Prefetch
from django.db import transaction
from persona.models import Jugador,JugadorCategoriaEquipo
from RegistroMedico.models import RegistroMedico, AntecedenteEnfermedades
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from Medico.models import Medico
from RegistroMedico.forms import *

class MedicoHomeView(LoginRequiredMixin, ListView):
    model = Jugador
    template_name = 'medico/medico_home.html'
    context_object_name = 'jugadores'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('persona__profile').prefetch_related(
            Prefetch('jugadorcategoriaequipo_set', queryset=JugadorCategoriaEquipo.objects.select_related(
                'categoria_equipo__categoria__torneo', 'categoria_equipo__equipo'))
        )
        
        # Filtrar según el término de búsqueda
        search_query = self.request.GET.get('search_query', '').strip()
        if not search_query:
            return queryset.none()

        queryset = queryset.filter(
            Q(persona__profile__dni__icontains=search_query) |
            Q(persona__profile__nombre__icontains=search_query) |
            Q(persona__profile__apellido__icontains=search_query)
        )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search_query', '')
        context['search_query'] = search_query

        try:
            context['medico'] = Medico.objects.get(profile=self.request.user.profile)
        except Medico.DoesNotExist:
            context['medico'] = None

        # List to hold player information with related medical forms
        jugadores_info = []
        for jugador in context['jugadores']:
            jugador_info = {
                'id': jugador.id,
                'edad': jugador.persona.profile.edad,
                'dni': jugador.persona.profile.dni,
                'nombre': jugador.persona.profile.nombre,
                'apellido': jugador.persona.profile.apellido,
                'direccion': jugador.persona.direccion,
                'telefono': jugador.persona.telefono,
                'grupo_sanguineo': jugador.grupo_sanguineo,
                'cobertura_medica': jugador.cobertura_medica,
                'numero_afiliado': jugador.numero_afiliado,
                'categorias_equipo': [],
                'antecedentes': [],
                'electro_basal_form': ElectroBasalForm() ,
                'electro_esfuerzo_form': None,
                'cardiovascular_form': None,
                'laboratorio_form': None,
                'oftalmologico_form': None,
                'torax_form': None,
            }

            # Registro médico y antecedentes
            registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
            if registro_medico:
                jugador_info['registro_medico_estado'] = registro_medico.estado

                # Obtener antecedentes
                antecedentes = AntecedenteEnfermedades.objects.filter(idfichaMedica=registro_medico)
                jugador_info['antecedentes'] = [
                    {'fue_operado': ant.fue_operado, 'toma_medicacion': ant.toma_medicacion}
                    for ant in antecedentes
                ]
                
                # Instanciar formularios con datos existentes, si están presentes
                jugador_info['electro_basal_form'] = ElectroBasalForm(
                    instance=ElectroBasal.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['electro_esfuerzo_form'] = ElectroEsfuerzoForm(
                    instance=ElectroEsfuerzo.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['cardiovascular_form'] = CardiovascularForm(
                    instance=Cardiovascular.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['laboratorio_form'] = LaboratorioForm(
                    instance=Laboratorio.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['oftalmologico_form'] = OftalmologicoForm(
                    instance=Oftalmologico.objects.filter(ficha_medica=registro_medico).first()
                )
                jugador_info['torax_form'] = ToraxForm(
                    instance=Torax.objects.filter(ficha_medica=registro_medico).first()
                )
            
            # Categorías y equipos asociados al jugador
            jugador_categoria_equipos = jugador.jugadorcategoriaequipo_set.all()
            jugador_info['categorias_equipo'] = [
                {
                    'nombre_categoria': jce.categoria_equipo.categoria.nombre,
                    'nombre_equipo': jce.categoria_equipo.equipo.nombre,
                    'torneo': jce.categoria_equipo.categoria.torneo.nombre
                } for jce in jugador_categoria_equipos
            ]
            
            jugadores_info.append(jugador_info)

        context['jugadores_info'] = jugadores_info
        return context
   

def electro_basal_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    electro_basal = ElectroBasal.objects.filter(ficha_medica=registro_medico).first()
    form_saved = False

    if request.method == 'POST':
        electro_basal_form = ElectroBasalForm(request.POST, instance=electro_basal)
        if electro_basal_form.is_valid():
            with transaction.atomic():
                electro_basal = electro_basal_form.save(commit=False)
                
                if not electro_basal.ficha_medica_id:
                    electro_basal.ficha_medica_id = registro_medico.idfichaMedica
                electro_basal.save()

                # Indica que el formulario se guardó correctamente
                form_saved = True

                # Puedes redirigir o mantener en la misma página según prefieras
                return redirect('electro_basal_view', jugador_id=jugador_id)
    else:
        electro_basal_form = ElectroBasalForm(instance=electro_basal)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'electro_basal_form': electro_basal_form,
        'form_saved': form_saved,
    })




def electro_esfuerzo_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

    # Si no se encuentra un registro médico para este jugador, manejarlo adecuadamente
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    # Verificar si ya existe un ElectroEsfuerzo asociado con este registro médico
    electro_esfuerzo = ElectroEsfuerzo.objects.filter(ficha_medica=registro_medico).first()

    # Si no existe, crear uno nuevo
    if not electro_esfuerzo:
        electro_esfuerzo = ElectroEsfuerzo(ficha_medica=registro_medico)

    if request.method == 'POST':
        electro_esfuerzo_form = ElectroEsfuerzoForm(request.POST, instance=electro_esfuerzo)
        if electro_esfuerzo_form.is_valid():
            with transaction.atomic():
                electro_esfuerzo = electro_esfuerzo_form.save(commit=False)
                # Asegurarse de asignar la ficha_medica si no está asignada
                if not electro_esfuerzo.ficha_medica_id:
                    electro_esfuerzo.ficha_medica_id = registro_medico.idfichaMedica
                electro_esfuerzo.save()
                # Mostrar mensaje de éxito, pero seguir en la misma página
                return render(request, 'medico/electro_esfuerzo_form.html', {
                    'form': electro_esfuerzo_form,
                    'jugador': jugador,
                    'success_message': "Formulario Electro Esfuerzo guardado con éxito"
                })
    else:
        electro_esfuerzo_form = ElectroEsfuerzoForm(instance=electro_esfuerzo)

    # Si ya hay un mensaje de éxito, lo pasamos a la plantilla
    success_message = request.GET.get('success_message', '')

def cardiovascular_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

    # Si no se encuentra un registro médico para este jugador, manejarlo adecuadamente
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    # Verificar si ya existe un Cardiovascular asociado con este registro médico
    cardiovascular = Cardiovascular.objects.filter(ficha_medica=registro_medico).first()

    # Si no existe, crear uno nuevo
    if not cardiovascular:
        cardiovascular = Cardiovascular(ficha_medica=registro_medico)

    if request.method == 'POST':
        cardiovascular_form = CardiovascularForm(request.POST, instance=cardiovascular)
        if cardiovascular_form.is_valid():
            with transaction.atomic():
                cardiovascular = cardiovascular_form.save(commit=False)
                # Asegurarse de asignar la ficha_medica si no está asignada
                if not cardiovascular.ficha_medica_id:
                    cardiovascular.ficha_medica_id = registro_medico.idfichaMedica
                cardiovascular.save()
              
    else:
        cardiovascular_form = CardiovascularForm(instance=cardiovascular)

    return render(request, 'medico/cardiovascular_form.html', {
        'form': cardiovascular_form,
        'jugador': jugador,
    })

def laboratorio_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

    # Si no se encuentra un registro médico para este jugador, manejarlo adecuadamente
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    # Verificar si ya existe un Laboratorio asociado con este registro médico
    laboratorio = Laboratorio.objects.filter(ficha_medica=registro_medico).first()

    # Si no existe, crear uno nuevo
    if not laboratorio:
        laboratorio = Laboratorio(ficha_medica=registro_medico)

    if request.method == 'POST':
        laboratorio_form = LaboratorioForm(request.POST, instance=laboratorio)
        if laboratorio_form.is_valid():
            with transaction.atomic():
                laboratorio = laboratorio_form.save(commit=False)
                # Asegurarse de asignar la ficha_medica si no está asignada
                if not laboratorio.ficha_medica_id:
                    laboratorio.ficha_medica_id = registro_medico.idfichaMedica
                laboratorio.save()
                return HttpResponse("Formulario Laboratorio guardado con éxito")
    else:
        laboratorio_form = LaboratorioForm(instance=laboratorio)

    return render(request, 'medico/laboratorio_form.html', {
        'form': laboratorio_form,
        'jugador': jugador,
    })

def torax_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

    # Si no se encuentra un registro médico para este jugador, manejarlo adecuadamente
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    # Verificar si ya existe un Torax asociado con este registro médico
    torax = Torax.objects.filter(ficha_medica=registro_medico).first()

    # Si no existe, crear uno nuevo
    if not torax:
        torax = Torax(ficha_medica=registro_medico)

    if request.method == 'POST':
        torax_form = ToraxForm(request.POST, instance=torax)
        if torax_form.is_valid():
            with transaction.atomic():
                torax = torax_form.save(commit=False)
                # Asegurarse de asignar la ficha_medica si no está asignada
                if not torax.ficha_medica_id:
                    torax.ficha_medica_id = registro_medico.idfichaMedica
                torax.save()
                return HttpResponse("Formulario Torax guardado con éxito")
    else:
        torax_form = ToraxForm(instance=torax)

    return render(request, 'medico/torax_form.html', {
        'form': torax_form,
        'jugador': jugador,
    })

def oftalmologico_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

    # Si no se encuentra un registro médico para este jugador, manejarlo adecuadamente
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    # Verificar si ya existe un Oftalmologico asociado con este registro médico
    oftalmologico = Oftalmologico.objects.filter(ficha_medica=registro_medico).first()

    # Si no existe, crear uno nuevo
    if not oftalmologico:
        oftalmologico = Oftalmologico(ficha_medica=registro_medico)

    if request.method == 'POST':
        oftalmologico_form = OftalmologicoForm(request.POST, instance=oftalmologico)
        if oftalmologico_form.is_valid():
            with transaction.atomic():
                oftalmologico = oftalmologico_form.save(commit=False)
                # Asegurarse de asignar la ficha_medica si no está asignada
                if not oftalmologico.ficha_medica_id:
                    oftalmologico.ficha_medica_id = registro_medico.idfichaMedica
                oftalmologico.save()
                return HttpResponse("Formulario Oftalmológico guardado con éxito")
    else:
        oftalmologico_form = OftalmologicoForm(instance=oftalmologico)

    return render(request, 'medico/oftalmologico_form.html', {
        'form': oftalmologico_form,
        'jugador': jugador,
    })
