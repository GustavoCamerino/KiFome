from django.urls import path
from .views_clean import (
    home, restaurante_detail,
    restaurante_signup, restaurante_dashboard,
    prato_create, prato_edit, prato_delete,
    categorias_manage, restaurante_profile, dashboard_data,
)

urlpatterns = [
    path('signup/', restaurante_signup, name='restaurante_signup'),
    path('dashboard/', restaurante_dashboard, name='restaurante_dashboard'),
    path('dashboard/data/', dashboard_data, name='restaurante_dashboard_data'),
    path('perfil/', restaurante_profile, name='restaurante_profile'),
    path('categorias/', categorias_manage, name='categorias_manage'),
    path('prato/novo/', prato_create, name='prato_create'),
    path('prato/<int:prato_id>/editar/', prato_edit, name='prato_edit'),
    path('prato/<int:prato_id>/remover/', prato_delete, name='prato_delete'),
    path('<int:restaurante_id>/', restaurante_detail, name='restaurante_detail'),
]
