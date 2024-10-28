from django.urls import path
from django.contrib.auth.views import LogoutView  # Importa LogoutView
from .views import user_login, dashboard, register

urlpatterns = [
    path('login/', user_login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),  # Usar LogoutView
]

