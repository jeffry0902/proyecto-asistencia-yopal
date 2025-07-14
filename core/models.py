from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    ROLES = (
        ('administrador', 'Administrador'),
        ('docente', 'Docente'),
        ('coordinador', 'Coordinador'),
        ('rector', 'Rector'),
    )
    rol = models.CharField(max_length=15, choices=ROLES, default='docente')

class Estudiante(models.Model):
    nombre_completo = models.CharField(max_length=200)
    codigo_estudiantil = models.CharField(max_length=50, unique=True, blank=True, null=True)
    # LA LÍNEA 'cursos = models.ManyToManyField...' HA SIDO ELIMINADA DE AQUÍ.

    def __str__(self):
        return self.nombre_completo

class Curso(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    # El campo 'docentes' ahora está aquí
    docentes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'rol': 'docente'},
        blank=True,
        related_name='cursos_asignados'
    )
    # Y también el campo 'estudiantes'
    estudiantes = models.ManyToManyField(Estudiante, blank=True, related_name='cursos')

    def __str__(self):
        return self.nombre

class Asistencia(models.Model):
    ESTADOS = (
        ('asistio', 'Asistió'),
        ('fallo', 'Falló'),
        ('tarde', 'Llegó Tarde'),
        ('excusado', 'Con Excusa'),
        ('evadido', 'Evadido'),
    )

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    docente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADOS)

    class Meta:
        unique_together = ('estudiante', 'curso', 'fecha', 'docente')

    def __str__(self):
        return f"{self.estudiante.nombre_completo} - {self.curso.nombre} - {self.docente.username} - {self.fecha} ({self.get_estado_display()})"