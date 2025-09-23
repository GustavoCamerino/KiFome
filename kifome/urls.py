from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from restaurantes.views_clean import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('clientes/', include('clientes.urls')),
    path('restaurantes/', include('restaurantes.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('avaliacoes/', include('avaliacoes.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
