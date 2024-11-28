
from django import forms
from django.contrib.auth.models import User
from .models import Profile

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repite Contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Profile  # Asegúrate de usar el modelo correcto aquí
        fields = ['nombre', 'apellido', 'dni', 'fecha_nacimiento', 'email', 'password1', 'password2']

    def clean_email(self):
        """ Verificar si el email ya está registrado. """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_dni(self):
        """ Verificar si el DNI ya está registrado. """
        dni = self.cleaned_data.get('dni')
        if Profile.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Este DNI ya está registrado.")
        return dni

    def clean_password2(self):
        """ Verificar que las contraseñas coincidan. """
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('Las contraseñas no son iguales.')
        return cd['password2']

    def save(self, commit=True):
        # Crear el usuario
        user = User(
            username=self.cleaned_data['email'],  # Usa el email como username
            email=self.cleaned_data['email'],
        )
        user.set_password(self.cleaned_data['password1'])  # Establece la contraseña
        if commit:
            user.save()  # Guarda el usuario

        # Crear el perfil asociado
        profile = Profile(
            user=user,
            nombre=self.cleaned_data['nombre'],
            apellido=self.cleaned_data['apellido'],
            dni=self.cleaned_data['dni'],
            fecha_nacimiento=self.cleaned_data['fecha_nacimiento'],
            email=self.cleaned_data['email'],
            rol='general'  # Asignar rol por defecto
        )
        if commit:
            profile.save()  # Guarda el perfil

        return user, profile 
