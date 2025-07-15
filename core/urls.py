# En core/urls.py
from django.urls import path, include 
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    path('dashboard/admin/', views.dashboard_admin_view, name='dashboard_admin'),
    path('dashboard/docente/', views.dashboard_docente_view, name='dashboard_docente'),
    path('dashboard/coordinador_rector/', views.dashboard_coordinador_rector_view, name='dashboard_coordinador_rector'),
    
    path('seleccionar-fecha/<int:asignacion_id>/', views.seleccionar_fecha_view, name='seleccionar_fecha'),
    path('asistencia/<int:asignacion_id>/', views.lista_asistencia_view, name='lista_asistencia'),
    path('historial/<int:asignacion_id>/', views.historial_asistencia_view, name='historial_asistencia'),
    path('historial/grupo/<int:grupo_id>/', views.historial_grupo_view, name='historial_grupo'),
]