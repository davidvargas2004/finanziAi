# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from finanzas_micro.recomendador import generate_cohere_recommendation, guardar_en_mongo # Asegúrate que esta ruta sea correcta
from datetime import datetime, date
from django.http import JsonResponse
from django.utils.timezone import localtime
import random
import json # Para el dashboard
from decimal import Decimal, InvalidOperation # Para manejar dinero con precisión

from .models import Notification, Consulta, FormularioFinanzas
from .forms import ConsultaForm
from django.db.models import Q


@login_required
def formulario_view(request):
    usuario = request.user
    nombre = usuario.get_full_name() or usuario.username
    
    context = {
        'nombre': nombre,
        'error': None,
    }

    if request.method == 'POST':
        try:
            ingresos = Decimal(request.POST.get('ingresos_mensuales', '0') or '0')
            
            gastos = {
                "Alimentacion": Decimal(request.POST.get('gasto_alimentacion', '0') or '0'),
                "Transporte": Decimal(request.POST.get('gasto_transporte', '0') or '0'),
                "Entretenimiento": Decimal(request.POST.get('gasto_entretenimiento', '0') or '0'),
                "Hogar": Decimal(request.POST.get('gasto_hogar', '0') or '0') 
            }
            
            meta_ahorro = Decimal(request.POST.get('meta_ahorro', '0') or '0')
            total_gastos = sum(gastos.values())
            ahorro_mensual = ingresos - total_gastos

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

            contexto_para_procesamiento = {
                "usuario_id": str(usuario.id), 
                "nombre": nombre,
                "ingresos_mensuales": float(ingresos), 
                "gastos_mensuales": {k: float(v) for k, v in gastos.items()},
                "metas_financieras": {"ahorro": float(meta_ahorro)},
                "ahorro_mensual": float(ahorro_mensual),
                "timestamp": datetime.now().isoformat()
            }
            
            recomendacion = generate_cohere_recommendation(contexto_para_procesamiento)
            lineas_recomendaciones = recomendacion.strip().splitlines()
            contexto_para_procesamiento["recomendacion_ia"] = recomendacion 
            guardar_en_mongo(contexto_para_procesamiento)

            FormularioFinanzas.objects.update_or_create(
                usuario_id=str(request.user.id), 
                defaults={
                    "nombre": nombre,
                    "ingresos_mensuales": ingresos,
                    "gasto_alimentacion": gastos["Alimentacion"],
                    "gasto_transporte": gastos["Transporte"],
                    "gasto_entretenimiento": gastos["Entretenimiento"],
                    "gasto_hogar": gastos["Hogar"],
                    "meta_ahorro": meta_ahorro,
                    "ahorro_mensual": ahorro_mensual,
                    "recomendaciones": recomendacion,
                    "fecha_actualizacion": date.today() 
                }
            )

            return render(request, "accounts/resultado.html", {
                "nombre": nombre,
                "total_gastos": total_gastos,
                "ahorro_mensual": ahorro_mensual,
                "meta_ahorro": meta_ahorro,
                "distribucion_gastos": distribucion_gastos_para_tabla,
                "lineas_recomendaciones": lineas_recomendaciones
            })

        except (ValueError, InvalidOperation): # Catch InvalidOperation for Decimal conversion
            messages.error(request, 'Por favor, ingresa solo números válidos.')
            context['post_data'] = request.POST
            context['error'] = 'Por favor, ingresa solo números válidos para los montos financieros.'
            return render(request, "accounts/formulario.html", context) 
        except Exception as e:
            print(f"ERROR GENERAL al procesar el formulario en formulario_view: {e}")
            messages.error(request, f'Ocurrió un error inesperado: {e}')
            context['error'] = f'Ocurrió un error inesperado: {e}'
            return render(request, "accounts/formulario.html", context)

    return render(request, "accounts/formulario.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            Notification.objects.create(user=user, message="Has iniciado sesión correctamente.")
            if not remember_me:
                request.session.set_expiry(0)
            return redirect('dashboard')
        else:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    login(request, user)
                    Notification.objects.create(user=user, message="Has iniciado sesión correctamente.")
                    if not remember_me:
                        request.session.set_expiry(0)
                    return redirect('dashboard')
            except User.DoesNotExist:
                pass 
            
            messages.error(request, 'Email o contraseña inválidos.')

    return render(request, 'accounts/login.html')

@login_required
def dashboard_view(request):
    current_year_int = datetime.now().year
    selected_year_str = request.GET.get('year', str(current_year_int))
    try:
        selected_year_int = int(selected_year_str)
    except ValueError:
        selected_year_int = current_year_int

    # Datos por defecto
    promedio_ingresos_val = Decimal('0.00')
    promedio_gastos_val = Decimal('0.00')
    promedio_ahorro_val = Decimal('0.00')
    mejor_mes_nombre_val = "N/A"
    mejor_mes_valor_val = Decimal('0.00')
    meta_ahorro_global_val = Decimal('0.00')
    consejos_list = ["No hay datos suficientes para generar consejos."]
    
    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    ingresos_mensuales_list = [0.0] * 12
    gastos_alimentacion_list = [0.0] * 12
    gastos_transporte_list = [0.0] * 12
    gastos_entretenimiento_list = [0.0] * 12
    gastos_hogar_list = [0.0] * 12
    gastos_totales_list = [0.0] * 12
    ahorros_list = [0.0] * 12

    try:
        datos_financieros = FormularioFinanzas.objects.get(usuario_id=str(request.user.id))
        
        # Ensure financial values from the model are treated as Decimal
        # This is a safeguard in case the model fields are FloatField or return floats,
        # or if values could be None.
        def to_decimal(value, default='0.0'):
            if value is None:
                return Decimal(default)
            try:
                return Decimal(str(value)) # str(value) is safer for float to Decimal conversion
            except InvalidOperation:
                return Decimal(default)

        promedio_ingresos_val = to_decimal(datos_financieros.ingresos_mensuales)
        
        gasto_alimentacion_actual = to_decimal(datos_financieros.gasto_alimentacion)
        gasto_transporte_actual = to_decimal(datos_financieros.gasto_transporte)
        gasto_entretenimiento_actual = to_decimal(datos_financieros.gasto_entretenimiento)
        gasto_hogar_actual = to_decimal(datos_financieros.gasto_hogar)
        
        promedio_gastos_val = (gasto_alimentacion_actual +
                               gasto_transporte_actual +
                               gasto_entretenimiento_actual +
                               gasto_hogar_actual)
        
        promedio_ahorro_val = promedio_ingresos_val - promedio_gastos_val 
        meta_ahorro_global_val = to_decimal(datos_financieros.meta_ahorro)

        current_month_index = datetime.now().month - 1 

        if hasattr(datos_financieros, 'fecha_actualizacion') and datos_financieros.fecha_actualizacion:
            record_year = datos_financieros.fecha_actualizacion.year
            record_month_index = datos_financieros.fecha_actualizacion.month -1
            if selected_year_int == record_year:
                 ingresos_mensuales_list[record_month_index] = float(promedio_ingresos_val)
                 gastos_alimentacion_list[record_month_index] = float(gasto_alimentacion_actual)
                 gastos_transporte_list[record_month_index] = float(gasto_transporte_actual)
                 gastos_entretenimiento_list[record_month_index] = float(gasto_entretenimiento_actual)
                 gastos_hogar_list[record_month_index] = float(gasto_hogar_actual)
                 gastos_totales_list[record_month_index] = float(promedio_gastos_val)
                 ahorros_list[record_month_index] = float(promedio_ahorro_val)
                 mejor_mes_nombre_val = meses_nombres[record_month_index]
                 mejor_mes_valor_val = promedio_ahorro_val 
        elif selected_year_int == current_year_int: 
            ingresos_mensuales_list[current_month_index] = float(promedio_ingresos_val)
            gastos_alimentacion_list[current_month_index] = float(gasto_alimentacion_actual)
            gastos_transporte_list[current_month_index] = float(gasto_transporte_actual)
            gastos_entretenimiento_list[current_month_index] = float(gasto_entretenimiento_actual)
            gastos_hogar_list[current_month_index] = float(gasto_hogar_actual)
            gastos_totales_list[current_month_index] = float(promedio_gastos_val)
            ahorros_list[current_month_index] = float(promedio_ahorro_val)
            mejor_mes_nombre_val = meses_nombres[current_month_index]
            mejor_mes_valor_val = promedio_ahorro_val
        
        consejos_list = []
        # All calculations below now use Decimal types consistently
        if promedio_ingresos_val > Decimal('0'): # Check against Decimal('0') for clarity
            if promedio_ahorro_val < (promedio_ingresos_val * Decimal('0.1')):
                consejos_list.append("Tu ahorro actual es un poco bajo respecto a tus ingresos. Intenta revisar gastos no esenciales.")
            if gasto_entretenimiento_actual > (promedio_ingresos_val * Decimal('0.2')):
                consejos_list.append("Considera moderar tus gastos en entretenimiento para mejorar tu capacidad de ahorro.")
        
        if not consejos_list and promedio_ingresos_val <= Decimal('0'): # If no income, different advice
             consejos_list.append("Parece que no has registrado ingresos. Por favor, actualiza tus datos en el formulario.")
        elif not consejos_list: # If income > 0 and no specific advice triggered
            consejos_list.append("¡Sigue así! Planificar tus finanzas es clave.")

        if datos_financieros.recomendaciones: 
            consejos_list.extend(datos_financieros.recomendaciones.strip().splitlines())

    except FormularioFinanzas.DoesNotExist:
        print(f"No se encontraron datos financieros para el usuario {request.user.id}")
        consejos_list = ["Ingresa tus datos en el formulario para ver un análisis financiero y consejos personalizados."]
    except Exception as e: # Catch other potential errors during data processing
        print(f"Error al procesar datos financieros para el dashboard: {e}")
        messages.error(request, "Hubo un error al cargar los datos del dashboard.")
        # Keep default values for context if processing fails


    chart_data_dict = {
        'meses': meses_nombres,
        'ingresos': ingresos_mensuales_list,
        'gastosAlimentacion': gastos_alimentacion_list,
        'gastosTransporte': gastos_transporte_list,
        'gastosEntretenimiento': gastos_entretenimiento_list,
        'gastosHogar': gastos_hogar_list,
        'gastosTotales': gastos_totales_list,
        'ahorros': ahorros_list,
    }

    available_years = [current_year_int, current_year_int - 1, current_year_int - 2]

    context = {
        'user': request.user, 
        'selected_year': selected_year_int,
        'available_years': available_years,
        'promedio_ingresos': f"{promedio_ingresos_val:.2f}",
        'promedio_gastos': f"{promedio_gastos_val:.2f}",
        'promedio_ahorro': f"{promedio_ahorro_val:.2f}",
        'mejor_mes_nombre': mejor_mes_nombre_val,
        'mejor_mes_valor': f"{mejor_mes_valor_val:.2f}",
        'meta_ahorro_global': f"{meta_ahorro_global_val:.2f}",
        'consejos': list(set(consejos_list)), 
        'chart_data_json': json.dumps(chart_data_dict)
    }
    return render(request, 'accounts/dashboard.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
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
            messages.error(request, 'Este email ya está registrado.')
            context['email_exists'] = True
            return render(request, 'accounts/signup.html', context)
        try:
            user = User.objects.create_user(
                username=email, email=email, password=password,
                first_name=first_name, last_name=last_name
            )
            login(request, user)
            Notification.objects.create(user=user, message="Bienvenido a Finanzia, tu cuenta ha sido creada.")
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Ocurrió un error: {str(e)}')
    return render(request, 'accounts/signup.html', context)

def password_reset_view(request):
    return render(request, 'accounts/password_reset.html')

@login_required
def notifications_view(request):
    notis = Notification.objects.filter(user=request.user).order_by('-created_at')
    data = [{'id': n.id, 'message': n.message, 
             'created_at': localtime(n.created_at).strftime('%Y-%m-%d %H:%M'), 
             'read': n.read} for n in notis]
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
    return render(request, 'accounts/comparativa_mensual.html')

@login_required
def historial_consultas(request):
    form = ConsultaForm()
    consultas = Consulta.objects.filter(usuario=request.user)
    query = request.GET.get('q')
    if query:
        consultas = consultas.filter(Q(consulta__icontains=query) | Q(resultado__icontains=query))
    consultas = consultas.order_by('-fecha')
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            nueva_consulta = form.save(commit=False)
            nueva_consulta.usuario = request.user
            nueva_consulta.resultado = procesar_consulta(nueva_consulta.consulta) 
            nueva_consulta.save()
            return redirect('historial_consultas')
    return render(request, 'accounts/historial.html', {'form': form, 'consultas': consultas, 'query': query or ''})

def procesar_consulta(texto):
    if 'saldo' in texto.lower(): return "Tu saldo es de $500. (Respuesta de ejemplo)"
    return random.choice([
        "No entendí tu consulta.", "Procesando...", "Excelente pregunta.", 
        "En cola...", "Trabajando en ello."
    ])

@login_required
def grafico_view(request):
    try:
        # Use .latest('fecha_actualizacion') if you added that field and want the truly latest
        datos = FormularioFinanzas.objects.filter(usuario_id=str(request.user.id)).latest('id') 
    except FormularioFinanzas.DoesNotExist:
        datos = None

    context_data = { # Valores por defecto
            "ingresos": Decimal('0.0'), "alimentacion": Decimal('0.0'), 
            "transporte": Decimal('0.0'), "entretenimiento": Decimal('0.0'),
            "hogar": Decimal('0.0'), "meta_ahorro": Decimal('0.0'), 
            "ahorro": Decimal('0.0')
    }
    if datos:
        # Helper to safely convert to Decimal
        def to_decimal_grafico(value, default='0.0'):
            if value is None: return Decimal(default)
            try: return Decimal(str(value))
            except InvalidOperation: return Decimal(default)

        ingresos = to_decimal_grafico(datos.ingresos_mensuales)
        alimentacion = to_decimal_grafico(datos.gasto_alimentacion)
        transporte = to_decimal_grafico(datos.gasto_transporte)
        entretenimiento = to_decimal_grafico(datos.gasto_entretenimiento)
        hogar = to_decimal_grafico(datos.gasto_hogar)
        meta_ahorro = to_decimal_grafico(datos.meta_ahorro)
        
        total_gastos = alimentacion + transporte + entretenimiento + hogar
        ahorro = ingresos - total_gastos
        
        context_data.update({
            "ingresos": ingresos, "alimentacion": alimentacion, "transporte": transporte,
            "entretenimiento": entretenimiento, "hogar": hogar, "meta_ahorro": meta_ahorro,
            "ahorro": ahorro
        })
    return render(request, "accounts/grafico.html", context_data)

@login_required
def eliminar_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id, usuario=request.user)
    consulta.delete()
    return redirect('historial_consultas')

def terms_of_service(request):
    return render(request, 'legal/terms_of_service.html')

def privacy_policy(request):
    return render(request, 'legal/privacy_policy.html')

from django.http import HttpResponse
from django.template.loader import render_to_string
# from weasyprint import HTML 
import tempfile 

@login_required 
def reporte_pdf(request):
    try:
        datos = FormularioFinanzas.objects.filter(usuario_id=str(request.user.id)).latest('id')
    except FormularioFinanzas.DoesNotExist:
        messages.error(request, "No hay datos financieros para generar el reporte.")
        return redirect('dashboard') 

    distribucion_gastos_pdf = []
    # Helper to safely convert to Decimal for PDF context
    def to_decimal_pdf(value, default='0.0'):
        if value is None: return Decimal(default)
        try: return Decimal(str(value))
        except InvalidOperation: return Decimal(default)

    ingresos_pdf = to_decimal_pdf(datos.ingresos_mensuales)
    gasto_alimentacion_pdf = to_decimal_pdf(datos.gasto_alimentacion)
    gasto_transporte_pdf = to_decimal_pdf(datos.gasto_transporte)
    gasto_entretenimiento_pdf = to_decimal_pdf(datos.gasto_entretenimiento)
    gasto_hogar_pdf = to_decimal_pdf(datos.gasto_hogar)
    ahorro_mensual_pdf = to_decimal_pdf(datos.ahorro_mensual)
    meta_ahorro_pdf = to_decimal_pdf(datos.meta_ahorro)

    if ingresos_pdf > Decimal('0'):
        categorias_gastos = {
            'Alimentación': gasto_alimentacion_pdf,
            'Transporte': gasto_transporte_pdf,
            'Entretenimiento': gasto_entretenimiento_pdf,
            'Hogar': gasto_hogar_pdf,
        }
        for categoria, valor in categorias_gastos.items():
            porcentaje = (valor / ingresos_pdf) * 100
            distribucion_gastos_pdf.append({'categoria': categoria, 'valor': valor, 'porcentaje': f"{porcentaje:.2f}"})
    else: 
         for categoria_nombre in ['Alimentación', 'Transporte', 'Entretenimiento', 'Hogar']:
             valor_gasto = locals().get(f"gasto_{categoria_nombre.lower()}_pdf", Decimal('0'))
             distribucion_gastos_pdf.append({'categoria': categoria_nombre, 'valor': valor_gasto, 'porcentaje': "0.00"})

    contexto_pdf = {
        'nombre': request.user.get_full_name() or request.user.username,
        'fecha_reporte': date.today().strftime("%d/%m/%Y"),
        'ingresos_mensuales': ingresos_pdf,
        'total_gastos': gasto_alimentacion_pdf + gasto_transporte_pdf + gasto_entretenimiento_pdf + gasto_hogar_pdf,
        'ahorro_mensual': ahorro_mensual_pdf, 
        'meta_ahorro': meta_ahorro_pdf,
        'distribucion_gastos_pdf': distribucion_gastos_pdf,
        'recomendaciones_pdf': datos.recomendaciones.strip().splitlines() if datos.recomendaciones else ["No hay recomendaciones específicas disponibles."]
    }

    html_string = render_to_string('accounts/reporte_template_pdf.html', contexto_pdf) 
    messages.info(request, "La generación de PDF está temporalmente desactivada. Mostrando datos en HTML (esto es para desarrollo).")
    return render(request, 'accounts/reporte_template_pdf.html', contexto_pdf)