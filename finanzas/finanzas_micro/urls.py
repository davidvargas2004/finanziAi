# finanzia/urls.py
from django.urls import path
from accounts import views

urlpatterns = [
    path('formulario/', views.formulario_view, name='formulario'),
    path('procesar-formulario/', views.formulario_view, name='procesar_formulario'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
]