from django.contrib import admin
from .models import Profile
from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nombre', 'apellido', 'dni', 'fecha_nacimiento', 'email', 'rol')  # Campos a mostrar en la lista
    search_fields = ('user__username', 'nombre', 'apellido', 'email')  # Campos por los que se puede buscar
    list_filter = ('rol',)  # Filtros por el rol
    list_editable = ('rol',)  # Permitir edición directa del rol en la lista
    
    def get_queryset(self, request):
        # Personalizar la consulta para incluir información relacionada
        qs = super().get_queryset(request)
        return qs.select_related('user')  # Mejorar el rendimiento al acceder a datos del usuario

admin.site.register(Profile, ProfileAdmin)
