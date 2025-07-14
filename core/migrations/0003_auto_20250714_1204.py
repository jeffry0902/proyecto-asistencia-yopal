# Al principio del archivo
from django.db import migrations

# Esta función creará nuestro superusuario
def create_superuser(apps, schema_editor):
    User = apps.get_model('core', 'CustomUser')

    # Creamos el usuario solo si no existe
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@ejemplo.com',
            password='adminasistencias', # ¡Cambia esto!
            rol='administrador'
        )

class Migration(migrations.Migration):

    # Reemplaza '0002_...' con el nombre del archivo de migración anterior al que creaste.
    # Por ejemplo, si tu migración anterior se llama '0002_alter_asistencia_estado.py',
    # la línea debe ser: dependencies = [('core', '0002_alter_asistencia_estado')]
    dependencies = [
        ('core', '0002_alter_asistencia_estado'), 
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]