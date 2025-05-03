from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from finanzas_micro.recomendador import generate_gemini_recommendation, guardar_en_mongo
from datetime import datetime

def formulario_view(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            usuario_id = request.POST.get('usuario_id')

            ingresos = float(request.POST.get('ingresos_mensuales') or 0)
            gastos = {
                "alimentacion": float(request.POST.get('gasto_alimentacion') or 0),
                "transporte": float(request.POST.get('gasto_transporte') or 0),
                "entretenimiento": float(request.POST.get('gasto_entretenimiento') or 0)
            }
            meta_ahorro = float(request.POST.get('meta_ahorro') or 0)
            total_gastos = sum(gastos.values())
            ahorro_mensual = ingresos - total_gastos

            contexto = {
                "usuario_id": usuario_id,
                "nombre": nombre,
                "ingresos_mensuales": ingresos,
                "gastos_mensuales": gastos,
                "metas_financieras": {"ahorro": meta_ahorro},
                "ahorro_mensual": ahorro_mensual,
                "timestamp": datetime.now().isoformat()
            }

            guardar_en_mongo(contexto)
            recomendacion = generate_gemini_recommendation(contexto)
            lineas_recomendaciones = recomendacion.strip().splitlines()

            return render(request, "accounts/resultado.html", {
                "nombre": nombre,
                "total_gastos": total_gastos,
                "ahorro_mensual": ahorro_mensual,
                "meta_ahorro": meta_ahorro,
                "lineas_recomendaciones": lineas_recomendaciones
            })

        except Exception as e:
            print("ERROR:", e)
            return render(request, "accounts/formulario.html", {
                "error": "Error al procesar el formulario. Asegúrate de ingresar valores válidos."
            })

    return render(request, "accounts/formulario.html")

           


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=email, password=password)
        if not user:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                username = User.objects.get(email=email).username
                user = authenticate(request, username=username, password=password)
            except:
                user = None

        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')

    return render(request, 'accounts/login.html')


@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def signup_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already registered and logged in.')
        return redirect('dashboard')

    context = {}

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/signup.html', context)

        if User.objects.filter(email=email).exists():
            context['email_exists'] = True
            return render(request, 'accounts/signup.html', context)

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Finanzia.')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    return render(request, 'accounts/signup.html', context)


def password_reset_view(request):
    return render(request, 'accounts/password_reset.html')
