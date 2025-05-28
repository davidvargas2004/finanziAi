from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Importaciones para las vistas de Simple JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')), # Incluye las URLs de tu app 'accounts'
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)), # Redirige la raíz a la página de login de accounts

    # ---- NUEVAS RUTAS PARA JWT ----
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('api/', include('accounts.api_urls')),
     
    # ---- FIN DE NUEVAS RUTAS ----
]

# Servir archivos estáticos durante el desarrollo (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    