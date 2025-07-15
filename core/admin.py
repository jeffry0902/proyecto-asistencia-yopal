from django.contrib import admin
from .models import CustomUser, Grupo, Materia, Asignacion, Estudiante, Asistencia
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# 1. Importamos las herramientas necesarias
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ManyToManyWidget

# --- Definición para el modelo CustomUser ---
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('rol',)}),
    )

# --- Clases para la gestión de Grupos y Asignaciones ---
class AsignacionInline(admin.TabularInline):
    model = Asignacion
    extra = 1

class GrupoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    filter_horizontal = ('estudiantes',)
    inlines = [AsignacionInline]

# --- 2. CONFIGURACIÓN PARA IMPORTAR ESTUDIANTES ---
class EstudianteResource(resources.ModelResource):
    # Le decimos cómo manejar la relación con los Grupos.
    # Buscará los grupos por su nombre en la columna 'grupos' del CSV.
    grupos = resources.Field(
        attribute='grupos',
        widget=ManyToManyWidget(Grupo, field='nombre', separator=',')
    )

    class Meta:
        model = Estudiante
        # Definimos las columnas que leerá nuestro archivo
        fields = ('id', 'nombre_completo', 'codigo_estudiantil', 'grupos')
        export_order = ('id', 'nombre_completo', 'codigo_estudiantil', 'grupos')

# Hacemos que el admin de Estudiante use esta configuración
class EstudianteAdmin(ImportExportModelAdmin):
    resource_class = EstudianteResource
    list_display = ('nombre_completo', 'codigo_estudiantil')
    search_fields = ('nombre_completo', 'codigo_estudiantil')


# --- 3. REGISTROS FINALES EN EL ADMIN ---
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Grupo, GrupoAdmin)
admin.site.register(Materia)
admin.site.register(Asignacion)
admin.site.register(Estudiante, EstudianteAdmin) # Usamos la nueva clase
admin.site.register(Asistencia)