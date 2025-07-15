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

# RENOMBRAMOS 'Curso' a 'Grupo'
class Grupo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    estudiantes = models.ManyToManyField('Estudiante', blank=True, related_name='grupos')

    def __str__(self):
        return self.nombre

# NUEVO MODELO para las materias
class Materia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

# NUEVO MODELO para conectar todo
class Asignacion(models.Model):
    docente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'rol': 'docente'})
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('docente', 'materia', 'grupo')

    def __str__(self):
        return f"{self.docente.username} - {self.materia.nombre} ({self.grupo.nombre})"

class Estudiante(models.Model):
    nombre_completo = models.CharField(max_length=200)
    codigo_estudiantil = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return self.nombre_completo

class Asistencia(models.Model):
    ESTADOS = (
        ('asistio', 'Asistió'),
        ('fallo', 'Falló'),
        ('tarde', 'Llegó Tarde'),
        ('excusado', 'Con Excusa'),
        ('evadido', 'Evadido'),
    )

    # AHORA LA ASISTENCIA SE LIGA A UNA ASIGNACIÓN ESPECÍFICA
    asignacion = models.ForeignKey(Asignacion, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    fecha = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADOS)

    class Meta:
        unique_together = ('asignacion', 'estudiante', 'fecha')

    def __str__(self):
        return f"{self.estudiante.nombre_completo} - {self.asignacion} - {self.fecha}"