from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from finanzas_micro.recomendador import generate_gemini_recommendation, guardar_en_mongo
from datetime import datetime
from .models import Notification
from django.http import JsonResponse
from django.utils.timezone import localtime
from .models import Consulta
from .models import FormularioFinanzas
from .forms import ConsultaForm
from django.db.models import Q
from django.shortcuts import get_object_or_404
import random


def formulario_view(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            usuario_id = request.POST.get('usuario_id')

            ingresos = float(request.POST.get('ingresos_mensuales') or 0)
            gasto_alimentacion = float(request.POST.get('gasto_alimentacion') or 0)
            gasto_transporte = float(request.POST.get('gasto_transporte') or 0)
            gasto_entretenimiento = float(request.POST.get('gasto_entretenimiento') or 0)
            meta_ahorro = float(request.POST.get('meta_ahorro') or 0)

            total_gastos = gasto_alimentacion + gasto_transporte + gasto_entretenimiento
            ahorro_mensual = ingresos - total_gastos

            contexto = {
                "usuario_id": usuario_id,
                "nombre": nombre,
                "ingresos_mensuales": ingresos,
                "gastos_mensuales": {
                    "alimentacion": gasto_alimentacion,
                    "transporte": gasto_transporte,
                    "entretenimiento": gasto_entretenimiento
                },
                "metas_financieras": {"ahorro": meta_ahorro},
                "ahorro_mensual": ahorro_mensual,
                "timestamp": datetime.now().isoformat()
            }

            # Obtener las recomendaciones
            recomendacion = generate_gemini_recommendation(contexto)
            lineas_recomendaciones = recomendacion.strip().splitlines()

            # Guardar en la base de datos SQLite
            FormularioFinanzas.objects.create(
                usuario_id=usuario_id,
                nombre=nombre,
                ingresos_mensuales=ingresos,
                gasto_alimentacion=gasto_alimentacion,
                gasto_transporte=gasto_transporte,
                gasto_entretenimiento=gasto_entretenimiento,
                meta_ahorro=meta_ahorro,
                ahorro_mensual=ahorro_mensual,
                recomendaciones=recomendacion
            )

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

            # Crear notificación al iniciar sesión
            Notification.objects.create(
                user=user,
                message="Has iniciado sesión correctamente."
            )

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

            # Crear notificación al registrarse
            Notification.objects.create(
                user=user,
                message="Bienvenido a Finanzia, tu cuenta ha sido creada."
            )

            messages.success(request, 'Account created successfully! Welcome to Finanzia.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    return render(request, 'accounts/signup.html', context)


def password_reset_view(request):
    return render(request, 'accounts/password_reset.html')


@login_required
def notifications_view(request):
    notis = Notification.objects.filter(user=request.user).order_by('-created_at')
    data = [
        {
            'id': n.id,
            'message': n.message,
            'created_at': localtime(n.created_at).strftime('%Y-%m-%d %H:%M'),
            'read': n.read
        }
        for n in notis
    ]
    return JsonResponse({'notifications': data})


@login_required
def mark_notification_read(request, notif_id):
    try:
        notif = Notification.objects.get(id=notif_id, user=request.user)
        notif.read = True
        notif.save()
        return JsonResponse({'status': 'ok'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)


def comparativa_mensual_view(request):
    """
    Vista simple que renderiza el template de comparativa mensual.
    Todo el procesamiento de datos y visualización se hace en el frontend
    con JavaScript.
    """
    return render(request, 'accounts/comparativa_mensual.html')

def grafico_view(request):
    return render(request, 'accounts/grafico.html')




#historial_consultas


@login_required
def historial_consultas(request):
    form = ConsultaForm()
    consultas = Consulta.objects.filter(usuario=request.user)

    # Búsqueda por palabra clave
    query = request.GET.get('q')
    if query:
        consultas = consultas.filter(
            Q(consulta__icontains=query) | Q(resultado__icontains=query)
        )

    # Ordenar de más reciente a más antigua
    consultas = consultas.order_by('-fecha')

    # Guardar consulta nueva si es POST
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            nueva_consulta = form.save(commit=False)
            nueva_consulta.usuario = request.user
            nueva_consulta.resultado = procesar_consulta(nueva_consulta.consulta)
            nueva_consulta.save()
            return redirect('historial_consultas')

    return render(request, 'accounts/historial.html', {
        'form': form,
        'consultas': consultas,
        'query': query or '',
    })

def procesar_consulta(texto):
    respuestas = [
        "Lo siento, no pude entender tu consulta.",
        "Estoy procesando tu solicitud, por favor espera.",
        "¡Excelente! Estás haciendo una gran pregunta. Déjame investigarlo.",
        "Tu consulta está en cola, te responderé pronto.",
        "Aún estoy trabajando en ello. Gracias por tu paciencia."
    ]
    
    if 'saldo' in texto.lower():
        return "Tu saldo es de $500."
    elif 'consulta' in texto.lower():
        return "Parece que estás buscando información sobre consultas. ¿En qué puedo ayudarte específicamente?"
    else:
        # Respuesta aleatoria 
        return random.choice(respuestas)


@login_required
def grafico_view(request):
    try:
        datos = FormularioFinanzas.objects.filter(usuario_id=request.user.id).latest('id')
    except FormularioFinanzas.DoesNotExist:
        datos = None

    if datos:
        context = {
            "alimentacion": datos.gasto_alimentacion,
            "transporte": datos.gasto_transporte,
            "entretenimiento": datos.gasto_entretenimiento,
        }
    else:
        context = {
            "alimentacion": 0,
            "transporte": 0,
            "entretenimiento": 0,
        }

    return render(request, "accounts/grafico.html", context) 


@login_required
def eliminar_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id, usuario=request.user)
    consulta.delete()
    return redirect('historial_consultas')

def terms_of_service(request):
    return render(request, 'legal/terms_of_service.html')

def privacy_policy(request):
    return render(request, 'legal/privacy_policy.html')