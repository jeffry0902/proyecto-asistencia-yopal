from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from .models import Grupo, Materia, Asignacion, Estudiante, Asistencia, CustomUser


def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')
        rol_seleccionado = request.POST.get('rol')
        user = authenticate(request, username=usuario, password=contrasena)
        if user is not None and user.rol.lower() == rol_seleccionado.lower():
            login(request, user)
            if user.rol == 'administrador':
                return redirect('dashboard_admin')
            elif user.rol == 'docente':
                return redirect('dashboard_docente')
            else:
                return redirect('dashboard_coordinador_rector')
        else:
            messages.error(request, 'Usuario, contraseña o rol incorrecto.')
            return redirect('login')
    return render(request, 'core/login.html')

@login_required
def dashboard_docente_view(request):
    # Ahora buscamos las asignaciones del docente, no los cursos
    asignaciones = Asignacion.objects.filter(docente=request.user).order_by('grupo__nombre', 'materia__nombre')
    contexto = {'asignaciones': asignaciones}
    return render(request, 'core/dashboard_docente.html', contexto)

@login_required
def seleccionar_fecha_view(request, asignacion_id):
    # Buscamos la asignacion, no el curso
    asignacion = get_object_or_404(Asignacion, id=asignacion_id)
    contexto = {
        'asignacion': asignacion
    }
    return render(request, 'core/seleccionar_fecha.html', contexto)

@login_required
def lista_asistencia_view(request, asignacion_id):
    asignacion = get_object_or_404(Asignacion, id=asignacion_id)
    # Obtenemos los estudiantes del grupo de esa asignación
    estudiantes = asignacion.grupo.estudiantes.all().order_by('nombre_completo')
    fecha_str = request.GET.get('fecha')
    if not fecha_str:
        messages.error(request, 'Debe seleccionar una fecha.')
        return redirect('seleccionar_fecha', asignacion_id=asignacion.id)
    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    if request.method == 'POST':
        for estudiante in estudiantes:
            estado_input_name = f'asistencia_{estudiante.id}'
            estado = request.POST.get(estado_input_name)
            if estado:
                Asistencia.objects.update_or_create(
                    asignacion=asignacion,
                    estudiante=estudiante,
                    fecha=fecha_obj,
                    defaults={'estado': estado}
                )
        messages.success(request, f'Asistencia para {asignacion.materia.nombre} del {fecha_obj.strftime("%d/%m/%Y")} guardada.')
        return redirect('dashboard_docente')
    contexto = {
        'asignacion': asignacion,
        'estudiantes': estudiantes,
        'fecha_seleccionada': fecha_obj
    }
    return render(request, 'core/lista_asistencia.html', contexto)

@login_required
def historial_asistencia_view(request, asignacion_id):
    asignacion_actual = get_object_or_404(Asignacion, id=asignacion_id)

    grupo_actual = asignacion_actual.grupo

    asistencias_query = Asistencia.objects.filter(asignacion__grupo=grupo_actual)

    if request.user.rol == 'docente':
        asistencias_query = asistencias_query.filter(asignacion=asignacion_actual)

    asistencias = asistencias_query.order_by('estudiante__nombre_completo', 'fecha', 'asignacion__materia__nombre')

    historial_agrupado = {}
    for asistencia in asistencias:
        if asistencia.estudiante not in historial_agrupado:
            historial_agrupado[asistencia.estudiante] = []
        historial_agrupado[asistencia.estudiante].append(asistencia)

    contexto = {
        'grupo': grupo_actual, # Pasamos el grupo para mostrar su nombre
        'historial': historial_agrupado,
        'rol_usuario': request.user.rol
    }

    return render(request, 'core/historial_asistencia.html', contexto)

@login_required
def dashboard_admin_view(request):
    return render(request, 'core/dashboard_admin.html')

@login_required
def dashboard_coordinador_rector_view(request):
    todos_los_grupos = Grupo.objects.all().order_by('nombre')
    contexto = {'grupos': todos_los_grupos}
    return render(request, 'core/dashboard_coordinador_rector.html', contexto)

@login_required
def historial_grupo_view(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    
    # Buscamos todas las asistencias cuyo grupo asignado sea el actual
    asistencias = Asistencia.objects.filter(asignacion__grupo=grupo).order_by('estudiante__nombre_completo', 'fecha', 'asignacion__materia__nombre')
    
    historial_agrupado = {}
    for asistencia in asistencias:
        if asistencia.estudiante not in historial_agrupado:
            historial_agrupado[asistencia.estudiante] = []
        historial_agrupado[asistencia.estudiante].append(asistencia)
            
    contexto = {
        'grupo': grupo, # Pasamos el grupo para mostrar su nombre
        'historial': historial_agrupado,
        'rol_usuario': request.user.rol
    }
    
    # Reutilizamos la misma plantilla del historial que ya tenemos
    return render(request, 'core/historial_asistencia.html', contexto)