from django.shortcuts import redirect, render
from .forms import LoginForm, UserRegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

@never_cache
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data  # Limpio los datos
            user = authenticate(request, username=cd['email'], password=cd['password'])  # Autenticación por email
            
            if user is not None:  # Si el usuario existe y está activo
                if user.is_active:
                    login(request, user)
                    
                    # Obtener el perfil del usuario y imprimir el rol
                    profile = user.profile  # Asegúrate de que el usuario tenga un perfil relacionado
                    print("Usuario autenticado:", profile.rol)  # Imprimir el rol del perfil
                    
                    # Redirigir según el rol del usuario
                    if profile.rol == 'medico':  # Verifica si el rol es médico
                        return redirect('medico_home')  # Cambia a la URL adecuada para médicos
                    elif profile.rol == 'general':  # Verifica si el rol es jugador
                        return redirect('registrar_persona')  # Cambia a la URL adecuada para jugadores
                    elif profile.rol == 'representante':
                        return redirect('representante_home')
                    else:
                        return redirect('home')  # Redirigir a una página predeterminada si no es médico ni jugador
                else:
                    return HttpResponse('El usuario no está activo')
            else:
                return HttpResponse('Usuario o contraseña incorrectos')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

@login_required
def dashboard(request):
    return redirect('persona/registrar')

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Guardar el usuario y su perfil
            user_form.save()  # Guarda tanto el usuario como el perfil asociado
            return render(request, 'account/register_done.html', {'new_user': user_form.cleaned_data['email']})
    else:
        user_form = UserRegistrationForm()

    # Mover este render fuera del bloque else, así se ejecuta tanto para GET como en caso de errores de validación
    return render(request, 'account/register.html', {'user_form': user_form})

def logout_view(request):
    return render(request, 'core/home.html')



def recover_Password(request):
    return render(request, 'account/password_change_form.html')