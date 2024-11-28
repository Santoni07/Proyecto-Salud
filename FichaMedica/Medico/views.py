from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import ListView
from django.db.models import Q, Prefetch
from django.db import transaction
from persona.models import Jugador,JugadorCategoriaEquipo
from RegistroMedico.models import RegistroMedico, AntecedenteEnfermedades
from django.contrib.auth.mixins import LoginRequiredMixin
from Medico.models import Medico
from RegistroMedico.forms import *
from weasyprint import HTML
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string


class MedicoHomeView(LoginRequiredMixin, ListView):
    model = Jugador
    template_name = 'medico/medico_home.html'
    context_object_name = 'jugadores'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('persona__profile').prefetch_related(
            Prefetch(
                'jugadorcategoriaequipo_set',
                queryset=JugadorCategoriaEquipo.objects.select_related(
                    'categoria_equipo__categoria__torneo', 'categoria_equipo__equipo'
                )
            )
        )
        
        # Obtener el término de búsqueda
        search_query = self.request.GET.get('search_query', '').strip()

        # Verificar si el término de búsqueda es un DNI
        if search_query:
            if search_query.isdigit() and len(search_query)  == 8:
                # Filtrar según el DNI
                queryset = queryset.filter(
                    Q(persona__profile__dni__icontains=search_query)
                )
            elif search_query.isalpha():
                # Búsqueda por nombre o apellido
                queryset = queryset.filter(
                    Q(persona__profile__nombre__icontains=search_query) |
                    Q(persona__profile__apellido__icontains=search_query)
                )    
            else:
                # Mostrar un mensaje de error si no cumple con el formato de DNI
                messages.error(self.request, "El valor ingresado para la busqueda por DNI es incorrecto. Debe contener exactamente 8 números.")
                return queryset.none()
        else:
            # Retornar un conjunto vacío si no se realiza ninguna búsqueda
            return queryset.none()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search_query', '')
        context['search_query'] = search_query

        try:
            context['medico'] = Medico.objects.get(profile=self.request.user.profile)
        except Medico.DoesNotExist:
            context['medico'] = None

                                   
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
                'estudios_medicos': [],
                'electro_basal_form': ElectroBasalForm() ,
                'electro_esfuerzo_form': None,
                'cardiovascular_form': None,
                'laboratorio_form': None,
                'oftalmologico_form': None,
                'torax_form': None,
                'registro_medico_form':None,
            }

            # Registro médico y antecedentes
            registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
            if registro_medico:
                
                 # Obtener estudios médicos
                estudios_medicos = EstudiosMedico.objects.filter(ficha_medica=registro_medico)
                jugador_info['estudios_medicos'] = [
                    {
                        'tipo': estudio.get_tipo_estudio_display(),
                        'archivo': estudio.archivo.url if estudio.archivo else None,
                        'observaciones': estudio.observaciones,
                    } for estudio in estudios_medicos
                ]

                jugador_info['registro_medico_estado'] = registro_medico.estado

                # Obtener antecedentes
                antecedentes = AntecedenteEnfermedades.objects.filter(idfichaMedica=registro_medico)
                jugador_info['antecedentes'] = [
                        {
                            'fue_operado': ant.fue_operado,
                            'toma_medicacion': ant.toma_medicacion,
                            'estuvo_internado': ant.estuvo_internado,
                            'sufre_hormigueos': ant.sufre_hormigueos,
                            'es_diabetico': ant.es_diabetico,
                            'es_asmatico': ant.es_amatico,
                            'es_alergico': ant.es_alergico,
                            'alerg_observ': ant.alerg_observ,
                            'antecedente_epilepsia': ant.antecedente_epilepsia,
                            'desviacion_columna': ant.desviacion_columna,
                            'dolor_cintura': ant.dolor_cintira,
                            'fracturas': ant.fracturas,
                            'dolores_articulares': ant.dolores_articulares,
                            'falta_aire': ant.falta_aire,
                            'traumatismos_craneo': ant.tramatismos_craneo,
                            'dolor_pecho': ant.dolor_pecho,
                            'perdida_conocimiento': ant.perdida_conocimiento,
                            'presion_arterial': ant.presion_arterial,
                            'muerte_subita_familiar': ant.muerte_subita_familiar,
                            'enfermedad_cardiaca_familiar': ant.enfermedad_cardiaca_familiar,
                            'soplo_cardiaco': ant.soplo_cardiaco,
                            'abstenerce_competencia': ant.abstenerce_competencia,
                            'antecedentes_coronarios_familiares': ant.antecedentes_coronarios_familiares,
                            'fumar_hipertension_diabetes': ant.fumar_hipertension_diabetes,
                            'consumo_cocaina_anabolicos': ant.consumo_cocaina_anabolicos,
                            'cca_observaciones': ant.cca_observaciones,
                        }
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
   
from django.http import JsonResponse

def electro_basal_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    
    if not registro_medico:
        return JsonResponse({"error": "No se encontró el registro médico del jugador."}, status=404)

    electro_basal = ElectroBasal.objects.filter(ficha_medica=registro_medico).first()
    form_saved = False
    form_complete = False

    if request.method == 'POST':
        electro_basal_form = ElectroBasalForm(request.POST, instance=electro_basal)
        if electro_basal_form.is_valid():
            with transaction.atomic():
                electro_basal = electro_basal_form.save(commit=False)
                
                if not electro_basal.ficha_medica_id:
                    electro_basal.ficha_medica_id = registro_medico.idfichaMedica
                electro_basal.save()

                form_saved = True

            # Si es una solicitud AJAX, devolvemos JSON en lugar de renderizar un template
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        electro_basal_form = ElectroBasalForm(instance=electro_basal)
        if electro_basal:
            form_complete = all(
                getattr(electro_basal, field.name) 
                for field in electro_basal_form
            )

    # Renderizar solo para solicitudes normales (no AJAX)
    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'electro_basal_form': electro_basal_form,
        'form_saved': form_saved,
        'form_complete': form_complete,
    })



def electro_esfuerzo_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    electro_esfuerzo = ElectroEsfuerzo.objects.filter(ficha_medica=registro_medico).first()
    if request.method == 'POST':
        electro_esfuerzo_form = ElectroEsfuerzoForm(request.POST, instance=electro_esfuerzo)
        if electro_esfuerzo_form.is_valid():
            with transaction.atomic():
                electro_esfuerzo = electro_esfuerzo_form.save(commit=False)
                electro_esfuerzo.ficha_medica = registro_medico
                electro_esfuerzo.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        electro_esfuerzo_form = ElectroEsfuerzoForm(instance=electro_esfuerzo)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'electro_esfuerzo_form': electro_esfuerzo_form,
    })


def cardiovascular_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    cardiovascular = Cardiovascular.objects.filter(ficha_medica=registro_medico).first()
    if request.method == 'POST':
        cardiovascular_form = CardiovascularForm(request.POST, instance=cardiovascular)
        if cardiovascular_form.is_valid():
            with transaction.atomic():
                cardiovascular = cardiovascular_form.save(commit=False)
                cardiovascular.ficha_medica = registro_medico
                cardiovascular.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        cardiovascular_form = CardiovascularForm(instance=cardiovascular)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'cardiovascular_form': cardiovascular_form,
    })


def laboratorio_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    laboratorio = Laboratorio.objects.filter(ficha_medica=registro_medico).first()
    if request.method == 'POST':
        laboratorio_form = LaboratorioForm(request.POST, instance=laboratorio)
        if laboratorio_form.is_valid():
            with transaction.atomic():
                laboratorio = laboratorio_form.save(commit=False)
                laboratorio.ficha_medica = registro_medico
                laboratorio.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        laboratorio_form = LaboratorioForm(instance=laboratorio)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'laboratorio_form': laboratorio_form,
    })


def torax_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    torax = Torax.objects.filter(ficha_medica=registro_medico).first()
    if request.method == 'POST':
        torax_form = ToraxForm(request.POST, instance=torax)
        if torax_form.is_valid():
            with transaction.atomic():
                torax = torax_form.save(commit=False)
                torax.ficha_medica = registro_medico
                torax.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        torax_form = ToraxForm(instance=torax)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'torax_form': torax_form,
    })


def oftalmologico_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    oftalmologico = Oftalmologico.objects.filter(ficha_medica=registro_medico).first()
    if request.method == 'POST':
        oftalmologico_form = OftalmologicoForm(request.POST, instance=oftalmologico)
        if oftalmologico_form.is_valid():
            with transaction.atomic():
                oftalmologico = oftalmologico_form.save(commit=False)
                oftalmologico.ficha_medica = registro_medico
                oftalmologico.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Formulario guardado exitosamente."})
    else:
        oftalmologico_form = OftalmologicoForm(instance=oftalmologico)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'oftalmologico_form': oftalmologico_form,
    })





def registro_medico_update_view(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    if request.method == 'POST':
        print(request.POST)  # Verifica los valores enviados en el formulario
        registro_medico_form = RegistroMedicoUpdateForm(request.POST, instance=registro_medico)
        if registro_medico_form.is_valid():
            with transaction.atomic():
                registro_medico = registro_medico_form.save(commit=False)
                
                # Obtener al médico logueado
                medico = Medico.objects.filter(profile=request.user.profile).first()
                if medico:
                    registro_medico.medico = medico  # Asignar el médico logueado

                registro_medico.save()
                return redirect('registro_medico_update_view', jugador_id=jugador_id)
        else:
            # Si el formulario no es válido, se puede imprimir para depurar
            print("Formulario no válido:", registro_medico_form.errors)
    else:
        registro_medico_form = RegistroMedicoUpdateForm(instance=registro_medico)

    return render(request, 'medico/medico_home.html', {
        'jugador': jugador,
        'registro_medico': registro_medico,  # Pasar el registro médico al contexto
        'registro_medico_form': registro_medico_form,
    })


def ficha_medica_views(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    registro_medico = RegistroMedico.objects.filter(jugador=jugador).first()

    # Obtener el rol del usuario logueado
    rol_usuario = request.user.profile.rol if hasattr(request.user, 'profile') else None
    if not registro_medico:
        return HttpResponse("No se encontró el registro médico del jugador.", status=404)

    if request.method == 'POST':
        registro_medico_form = RegistroMedicoUpdateForm(request.POST, instance=registro_medico)
        if registro_medico_form.is_valid():
            registro_medico = registro_medico_form.save(commit=False)
            medico = Medico.objects.filter(profile=request.user.profile).first()
            if medico:
                registro_medico.medico = medico
            registro_medico.save()
            return redirect('ficha_medica', jugador_id=jugador_id)
    else:
        registro_medico_form = RegistroMedicoUpdateForm(instance=registro_medico)

    antecedentes = AntecedenteEnfermedades.objects.filter(idfichaMedica=registro_medico)
    electro_basal = ElectroBasal.objects.filter(ficha_medica=registro_medico).first()
    electro_esfuerzo = ElectroEsfuerzo.objects.filter(ficha_medica=registro_medico).first()
    cardiovascular = Cardiovascular.objects.filter(ficha_medica=registro_medico).first()
    laboratorio = Laboratorio.objects.filter(ficha_medica=registro_medico).first()
    oftalmologico = Oftalmologico.objects.filter(ficha_medica=registro_medico).first()
    torax = Torax.objects.filter(ficha_medica=registro_medico).first()

    # Convertir URLs relativas de imágenes en absolutas
    for categoria in jugador.jugadorcategoriaequipo_set.all():
        if categoria.categoria_equipo.categoria.torneo.imagen:
             categoria.categoria_equipo.categoria.torneo.imagen_url = request.build_absolute_uri(
                categoria.categoria_equipo.categoria.torneo.imagen.url
            )
    
    if registro_medico.medico and registro_medico.medico.firma:
        registro_medico.medico.firma = request.build_absolute_uri(registro_medico.medico.firma.url)

    jugador_info = {
        'id': jugador.id,
        'edad': jugador.persona.profile.edad,
        'dni': jugador.persona.profile.dni,
        'nombre': jugador.persona.profile.nombre,
        'rol_usuario': jugador.persona.profile.rol,
        'apellido': jugador.persona.profile.apellido,
        'direccion': jugador.persona.direccion,
        'telefono': jugador.persona.telefono,
        'grupo_sanguineo': jugador.grupo_sanguineo,
        'cobertura_medica': jugador.cobertura_medica,
        'numero_afiliado': jugador.numero_afiliado,
        'categorias_equipo': [
            {
                'nombre_categoria': jce.categoria_equipo.categoria.nombre,
                'nombre_equipo': jce.categoria_equipo.equipo.nombre,
                'torneo': jce.categoria_equipo.categoria.torneo.nombre,
                 'imagen': jce.categoria_equipo.categoria.torneo.imagen.url if jce.categoria_equipo.categoria.torneo.imagen else None,
                'descripcion': jce.categoria_equipo.categoria.torneo.descripcion,
                'direccion': jce.categoria_equipo.categoria.torneo.direccion,
                'telefono': jce.categoria_equipo.categoria.torneo.telefono,
            }
            for jce in jugador.jugadorcategoriaequipo_set.all()
        ],
        'antecedentes': [{'fue_operado': ant.fue_operado,
                            'toma_medicacion': ant.toma_medicacion,
                            'estuvo_internado': ant.estuvo_internado,
                            'sufre_hormigueos': ant.sufre_hormigueos,
                            'es_diabetico': ant.es_diabetico,
                            'es_asmatico': ant.es_amatico,
                            'es_alergico': ant.es_alergico,
                            'alerg_observ': ant.alerg_observ,
                            'antecedente_epilepsia': ant.antecedente_epilepsia,
                            'desviacion_columna': ant.desviacion_columna,
                            'dolor_cintura': ant.dolor_cintira,
                            'fracturas': ant.fracturas,
                            'dolores_articulares': ant.dolores_articulares,
                            'falta_aire': ant.falta_aire,
                            'traumatismos_craneo': ant.tramatismos_craneo,
                            'dolor_pecho': ant.dolor_pecho,
                            'perdida_conocimiento': ant.perdida_conocimiento,
                            'presion_arterial': ant.presion_arterial,
                            'muerte_subita_familiar': ant.muerte_subita_familiar,
                            'enfermedad_cardiaca_familiar': ant.enfermedad_cardiaca_familiar,
                            'soplo_cardiaco': ant.soplo_cardiaco,
                            'abstenerce_competencia': ant.abstenerce_competencia,
                            'antecedentes_coronarios_familiares': ant.antecedentes_coronarios_familiares,
                            'fumar_hipertension_diabetes': ant.fumar_hipertension_diabetes,
                            'consumo_cocaina_anabolicos': ant.consumo_cocaina_anabolicos,
                            'cca_observaciones': ant.cca_observaciones,} for ant in antecedentes],
        'electro_basal_form': ElectroBasalForm(instance=electro_basal),
        'electro_esfuerzo_form': ElectroEsfuerzoForm(instance=electro_esfuerzo),
        'cardiovascular_form': CardiovascularForm(instance=cardiovascular),
        'laboratorio_form': LaboratorioForm(instance=laboratorio),
        'oftalmologico_form': OftalmologicoForm(instance=oftalmologico),
        'torax_form': ToraxForm(instance=torax),
        'registro_medico_form': registro_medico_form,
    }

    # Generar y descargar PDF si se solicita
    if request.GET.get('descargar_pdf') == 'true':
        html_content = render_to_string('medico/medico_views.html', {
            'jugador_info': jugador_info,
            'registro_medico': registro_medico,
        })

        # Extraer solo el contenido del bloque de HTML
        start_tag = '<section id="content">'
        end_tag = '</section>'
        content_start = html_content.find(start_tag)
        content_end = html_content.find(end_tag) + len(end_tag)
        content_to_pdf = html_content[content_start:content_end]

        html_string = f"""
                        <!DOCTYPE html>
                        <html lang="es">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Ficha Médica</title>
                            <style>
                                body {{
                                    font-family: 'Arial', sans-serif;
                                    font-size: 10px;
                                    color: #333;
                                    margin: 0;
                                    padding: 0;
                                }}

                                /* Contenedor principal */
                                .container {{
                                    padding: 10px;
                                    margin: 0 auto;
                                    max-width: 760px;
                                }}

                                /* Encabezados */
                                h1, h2, h3, h4 {{
                                    color: #0056b3;
                                    text-align: center;
                                    margin: 5px 0;
                                    font-weight: bold;
                                    font-size: 14px;
                                }}

                                /* Tarjetas */
                                .card {{
                                    
                                    margin-bottom: 10px;
                                    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
                                }}

                                .card-header {{
                                    background-color: #f7f7f7;
                                   
                                    text-align: center;
                                    font-size: 12px;
                                    font-weight: bold;
                                }}

                                .card-body {{
                                    padding: 0px;
                                    line-height: 1.4;
                                    font-size: 10px;
                                }}

                                /* Filas y columnas */
                                .row {{
                                    display: flex;
                                    flex-wrap: wrap;
                                    margin: 0 -8px;
                                }}

                                .col-md-6, .col-md-4, .col-md-3, .col-md-9 {{
                                    padding: 0px;
                                    flex: 1;
                                }}

                                /* Imágenes */
                                img {{
                                    max-width: 200px;
                                    height: auto;
                                 
                                }}

                                /* Tablas */
                                table {{
                                    width: 60%;
                                    
                                    margin-top: 10px;
                                }}

                                table th, table td {{
                                    
                                    
                                    text-align: left;
                                    font-size: 10px;
                                }}

                                table th {{
                                    background-color: #f1f1f1;
                                    font-weight: bold;
                                }}

                                /* Resaltado */
                                strong {{
                                    color: black;
                                }}
                            </style>
                        </head>
                        <body>
                            {content_to_pdf}
                        </body>
                        </html>
                        """
        

        # Crear PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ficha_medica_{jugador_info['apellido']}_{jugador_info['nombre']}.pdf"'
        return response

    context = {
        'jugador_info': jugador_info,
        'registro_medico': registro_medico,
        'rol_usuario': rol_usuario,
    }
    return render(request, 'medico/medico_views.html', context)

