from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Necesario para DEBUG y static
from django.conf.urls.static import static # Necesario para static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')), # Incluye las URLs de tu app 'accounts'
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)), # Redirige la raíz a la página de login de accounts
]

# Servir archivos estáticos durante el desarrollo (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Si también usas archivos subidos por usuarios (MEDIA_FILES):
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)