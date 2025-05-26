# accounts/views.py (VERSIÓN UNIFICADA Y CORREGIDA)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from finanzas_micro.recomendador import generate_cohere_recommendation, guardar_en_mongo
from datetime import datetime
from django.http import JsonResponse
from django.utils.timezone import localtime
import random


from .models import Notification, Consulta, FormularioFinanzas
from .forms import ConsultaForm
from django.db.models import Q


@login_required 
def formulario_view(request):
    """
    Vista para manejar el formulario de ingresos y gastos del usuario.
    Procesa los datos, calcula métricas financieras, guarda en MongoDB Atlas,
    y genera recomendaciones de IA (Cohere).
    """
    
    # --- Lógica para obtener el nombre del usuario siempre, antes del POST/GET ---
    usuario = request.user
    nombre = usuario.get_full_name() or usuario.username
    
    # Prepara el contexto inicial con el nombre del usuario
    context = {
        'nombre': nombre,
        'error': None, # Por defecto no hay error
    }
    # --- Fin de la lógica para obtener el nombre ---

    if request.method == 'POST':
        try:
            usuario_id = str(usuario.id)

            # Obtener datos del formulario y convertirlos a float
            ingresos = float(request.POST.get('ingresos_mensuales', 0) or 0)
            
            # Recopilar gastos por categoría con nombres de claves consistentes
            gastos = {
                "Alimentacion": float(request.POST.get('gasto_alimentacion', 0) or 0),
                "Transporte": float(request.POST.get('gasto_transporte', 0) or 0),
                "Entretenimiento": float(request.POST.get('gasto_entretenimiento', 0) or 0),
                "Hogar": float(request.POST.get('gasto_hogar', 0) or 0) 
            }
            
            meta_ahorro = float(request.POST.get('meta_ahorro', 0) or 0)

            # Calcular el total de gastos sumando los valores del diccionario
            total_gastos = sum(gastos.values())
            ahorro_mensual = ingresos - total_gastos

            # Preparar los datos de distribución de gastos para la tabla HTML
            distribucion_gastos_para_tabla = []
            if ingresos > 0:
                for categoria, valor in gastos.items():
                    porcentaje = (valor / ingresos) * 100
                    distribucion_gastos_para_tabla.append({
                        'categoria': categoria,
                        'porcentaje': f"{porcentaje:.2f}"
                    })
            else:
                for categoria, _ in gastos.items():
                    distribucion_gastos_para_tabla.append({
                        'categoria': categoria,
                        'porcentaje': "0.00"
                    })

            # Datos para guardar en MongoDB Atlas y pasar a la API de Cohere
            contexto_para_procesamiento = {
                "usuario_id": usuario_id,
                "nombre": nombre, # El nombre ya está disponible aquí
                "ingresos_mensuales": ingresos,
                "gastos_mensuales": gastos, # Pasamos el diccionario completo de gastos por categoría
                "metas_financieras": {"ahorro": meta_ahorro},
                "ahorro_mensual": ahorro_mensual,
                "timestamp": datetime.now().isoformat()
            }
            
            # Generar recomendaciones usando Cohere
            recomendacion = generate_cohere_recommendation(contexto_para_procesamiento)
            lineas_recomendaciones = recomendacion.strip().splitlines()

            # AÑADIR LA RECOMENDACIÓN AL DICCIONARIO ANTES DE GUARDAR EN MONGODB ATLAS
            contexto_para_procesamiento["recomendacion_ia"] = recomendacion 

            # Guardar los datos completos (incluyendo la recomendación) en MongoDB Atlas
            guardar_en_mongo(contexto_para_procesamiento)

            # Renderizar la plantilla de resultados con todos los datos necesarios
            return render(request, "accounts/resultado.html", {
                "nombre": nombre,
                "total_gastos": total_gastos,
                "ahorro_mensual": ahorro_mensual,
                "meta_ahorro": meta_ahorro,
                "distribucion_gastos": distribucion_gastos_para_tabla, # Para la tabla de porcentajes
                "lineas_recomendaciones": lineas_recomendaciones
            })

        except ValueError:
            messages.error(request, 'Por favor, ingresa solo números válidos para los ingresos, gastos y metas.')
            # Si hay un error de validación, se debe re-renderizar el formulario
            # y pasar los datos POST para que los campos se pre-rellenen.
            # Asegúrate de pasar 'nombre' también en este caso.
            context['post_data'] = request.POST
            context['error'] = 'Por favor, ingresa solo números válidos para los ingresos, gastos y metas.'
            return render(request, "accounts/formulario.html", context) 
        except Exception as e:
            print(f"ERROR GENERAL al procesar el formulario en formulario_view: {e}")
            messages.error(request, f'Ocurrió un error inesperado al procesar el formulario. Por favor, inténtalo de nuevo. Detalles: {e}')
            # Si hay un error general, re-renderizar el formulario y pasar 'nombre'.
            context['error'] = f'Ocurrió un error inesperado al procesar el formulario. Por favor, inténtalo de nuevo. Detalles: {e}'
            return render(request, "accounts/formulario.html", context)

    # Si el método es GET (o si llegamos aquí después de un POST con errores no manejados por las excepciones anteriores)
    # se renderiza el formulario, y el 'nombre' ya está en el 'context' inicial.
    return render(request, "accounts/formulario.html", context)


def login_view(request):
    """
    Vista para manejar el inicio de sesión de usuarios.
    """
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
            except User.DoesNotExist: # Captura la excepción específica
                user = None

        if user is not None:
            login(request, user)
            Notification.objects.create(user=user, message="Has iniciado sesión correctamente.")
            if not remember_me:
                request.session.set_expiry(0)
            return redirect('dashboard')
        else:
            messages.error(request, 'Email o contraseña inválidos. Por favor, inténtalo de nuevo.')

    return render(request, 'accounts/login.html')

@login_required
def dashboard_view(request):
    """
    Vista del dashboard principal para usuarios autenticados.
    """
    return render(request, 'accounts/dashboard.html')

def logout_view(request):
    """
    Vista para cerrar la sesión del usuario.
    """
    logout(request)
    return redirect('login')

def signup_view(request):
    """
    Vista para el registro de nuevos usuarios.
    """
    if request.user.is_authenticated:
        messages.info(request, 'Ya estás registrado e has iniciado sesión.')
        return redirect('dashboard')

    context = {}

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'accounts/signup.html', context)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este email ya está registrado. Por favor, inicia sesión o usa otro email.')
            context['email_exists'] = True
            return render(request, 'accounts/signup.html', context)

        try:
            user = User.objects.create_user(
                username=email, # Usar el email como username para la creación
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            Notification.objects.create(user=user, message="Bienvenido a Finanzia, tu cuenta ha sido creada.")
            messages.success(request, '¡Cuenta creada exitosamente! Bienvenido a Finanzia.')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrar la cuenta: {str(e)}')

    return render(request, 'accounts/signup.html', context)

def password_reset_view(request):
    """
    Vista para la página de restablecimiento de contraseña (funcionalidad no implementada aquí, es solo un placeholder).
    """
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

@login_required
def historial_consultas(request):
    form = ConsultaForm()
    consultas = Consulta.objects.filter(usuario=request.user)

    query = request.GET.get('q')
    if query:
        consultas = consultas.filter(
            Q(consulta__icontains=query) | Q(resultado__icontains=query)
        )

    consultas = consultas.order_by('-fecha')

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
        return random.choice(respuestas)


@login_required
def grafico_view(request): 
    try:
        # Obtener los datos más recientes del usuario logueado
        datos = FormularioFinanzas.objects.filter(usuario_id=request.user.id).latest('id')
    except FormularioFinanzas.DoesNotExist:
        datos = None

    if datos:
        context = {
            "alimentacion": datos.gasto_alimentacion,
            "transporte": datos.gasto_transporte,
            "entretenimiento": datos.gasto_entretenimiento,
            # Asegúrate de incluir 'gasto_hogar' aquí si lo estás usando en tu modelo
            # "hogar": datos.gasto_hogar,
        }
    else:
        context = {
            "alimentacion": 0,
            "transporte": 0,
            "entretenimiento": 0,
            # "hogar": 0,
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


#pdf generation view
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import RegistroFinanciero, GastoCategoria
import tempfile

def generar_pdf(request):
    usuario_id = request.user.id

    try:
        registro = RegistroFinanciero.objects.get(usuario_id=usuario_id)
    except RegistroFinanciero.DoesNotExist:
        return HttpResponse("No hay datos registrados.", status=404)

    categorias = GastoCategoria.objects.filter(registro=registro)

    
    # Imprimir para depuración
    print(f"Registro encontrado: {registro}")

    context = {
        'total_gastos': registro.total_gastos,
        'ahorro_mensual': registro.ahorro_mensual,
        'meta_ahorro': registro.meta_ahorro,
        'distribucion': [
            {'categoria': c.categoria, 'porcentaje': c.porcentaje} for c in categorias
        ]
    }

    html_string = render_to_string("reporte_pdf.html", context)

    with tempfile.NamedTemporaryFile(delete=True) as output:
        HTML(string=html_string).write_pdf(output.name)
        output.seek(0)
        response = HttpResponse(output.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_financiero.pdf"'
        return response

