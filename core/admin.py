from django.contrib import admin
from .models import CustomUser, Curso, Estudiante, Asistencia
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ManyToManyWidget

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('rol',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('rol',)}),
    )

class EstudianteResource(resources.ModelResource):
    cursos = resources.Field(
        attribute='cursos',
        widget=ManyToManyWidget(Curso, field='nombre', separator=',')
    )
    class Meta:
        model = Estudiante
        fields = ('id', 'nombre_completo', 'codigo_estudiantil', 'cursos')

class EstudianteAdmin(ImportExportModelAdmin):
    resource_class = EstudianteResource
    list_display = ('nombre_completo', 'codigo_estudiantil')
    search_fields = ('nombre_completo', 'codigo_estudiantil')

class CursoAdmin(ImportExportModelAdmin):
    list_display = ('nombre',)
    filter_horizontal = ('estudiantes', 'docentes',)
    search_fields = ('nombre',)

if admin.site.is_registered(Estudiante):
    admin.site.unregister(Estudiante)
if admin.site.is_registered(Curso):
    admin.site.unregister(Curso)
if admin.site.is_registered(CustomUser):
    admin.site.unregister(CustomUser)

admin.site.register(Estudiante, EstudianteAdmin)
admin.site.register(Curso, CursoAdmin)
admin.site.register(CustomUser, CustomUserAdmin) # <-- Usamos nuestra clase personalizada
admin.site.register(Asistencia)