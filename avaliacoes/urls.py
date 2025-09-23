from django.urls import path
from .views import avaliar_restaurante

urlpatterns = [
    path('<int:restaurante_id>/avaliar/', avaliar_restaurante, name='avaliar_restaurante'),
]

