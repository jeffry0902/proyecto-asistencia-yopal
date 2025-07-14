# En core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Curso, Asistencia, Estudiante
from datetime import datetime # Asegúrate de importar datetime

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
            messages.error(request, 'Usuario, contraseña o rol incorrecto. Por favor, intente de nuevo.')
            return redirect('login')
    return render(request, 'core/login.html')

@login_required
def lista_asistencia_view(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    estudiantes = curso.estudiantes.all().order_by('nombre_completo')

    fecha_str = request.GET.get('fecha')

    if not fecha_str:
        messages.error(request, 'Debe seleccionar una fecha.')
        return redirect('seleccionar_fecha', curso_id=curso.id)

    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()

    if request.method == 'POST':
        for key, estado in request.POST.items():
            if key.startswith('asistencia_'):
                try:
                    estudiante_id = int(key.split('_')[1])
                    estudiante_obj = Estudiante.objects.get(id=estudiante_id)

                    Asistencia.objects.update_or_create(
                        estudiante=estudiante_obj,
                        curso=curso,
                        fecha=fecha_obj, 
                        docente=request.user,
                        defaults={'estado': estado}
                    )
                except (ValueError, IndexError, Estudiante.DoesNotExist):
                    continue

        messages.success(request, f'Asistencia para el {fecha_obj.strftime("%d/%m/%Y")} guardada exitosamente.')
        return redirect('dashboard_docente')

    contexto = {
        'curso': curso,
        'estudiantes': estudiantes,
        'fecha_seleccionada': fecha_obj # Pasamos la fecha a la plantilla para mostrarla
    }
    return render(request, 'core/lista_asistencia.html', contexto)
@login_required
def dashboard_docente_view(request):
    cursos_asignados = Curso.objects.filter(docentes=request.user)
    contexto = {
        'cursos': cursos_asignados
    }
    return render(request, 'core/dashboard_docente.html', contexto)

@login_required
def historial_asistencia_view(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    # --- INICIO DE LA CORRECCIÓN ---
    # Por defecto, obtenemos todos los registros del curso
    asistencias_query = Asistencia.objects.filter(curso=curso)

    # Si el usuario es un docente, filtramos para ver solo sus registros
    if request.user.rol == 'docente':
        asistencias_query = asistencias_query.filter(docente=request.user)

    # Si es coordinador o rector, la consulta se queda como está (todos los registros del curso)

    asistencias = asistencias_query.order_by('estudiante__nombre_completo', 'fecha')
    # --- FIN DE LA CORRECCIÓN ---

    historial_agrupado = {}
    for asistencia in asistencias:
        if asistencia.estudiante not in historial_agrupado:
            historial_agrupado[asistencia.estudiante] = []
        historial_agrupado[asistencia.estudiante].append(asistencia)

    contexto = {
        'curso': curso,
        'historial': historial_agrupado,
        'rol_usuario': request.user.rol # Pasamos el rol para arreglar el botón "Volver"
    }

    return render(request, 'core/historial_asistencia.html', contexto)

@login_required
def dashboard_admin_view(request):
    return render(request, 'core/dashboard_admin.html')

@login_required
def dashboard_coordinador_rector_view(request):
    # Obtenemos TODOS los cursos del colegio, ordenados por nombre.
    todos_los_cursos = Curso.objects.all().order_by('nombre')

    contexto = {
        'cursos': todos_los_cursos
    }

    return render(request, 'core/dashboard_coordinador_rector.html', contexto)

@login_required
def seleccionar_fecha_view(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    contexto = {
        'curso': curso
    }
    return render(request, 'core/seleccionar_fecha.html', contexto)