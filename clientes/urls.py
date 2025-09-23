from django.urls import path
from .views import cliente_signup, cliente_dashboard, cliente_profile

urlpatterns = [
    path('signup/', cliente_signup, name='cliente_signup'),
    path('dashboard/', cliente_dashboard, name='cliente_dashboard'),
    path('perfil/', cliente_profile, name='cliente_profile'),
]
