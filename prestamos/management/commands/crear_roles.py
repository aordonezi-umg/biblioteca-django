from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

# Qué acciones puede hacer cada rol en cada app
ROLES = {
    "Bibliotecario": {
        "catalogo": ["add", "change", "delete", "view"],
        "prestamos": ["add", "change", "delete", "view"],
    },
    "Estudiante": {
        "catalogo": ["view"],
        "prestamos": ["view"],
    },
}


class Command(BaseCommand):
    help = "Crea o actualiza los grupos Bibliotecario y Estudiante con sus permisos."

    def handle(self, *args, **options):
        for nombre_grupo, permisos_por_app in ROLES.items():
            grupo, creado = Group.objects.get_or_create(name=nombre_grupo)

            permisos_de_las_apps = Permission.objects.filter(
                content_type__app_label__in=permisos_por_app.keys()
            ).select_related("content_type")

            # El codename tiene la forma "accion_modelo", por ejemplo "add_libro"
            seleccionados = [
                permiso
                for permiso in permisos_de_las_apps
                if permiso.codename.split("_")[0]
                in permisos_por_app[permiso.content_type.app_label]
            ]

            grupo.permissions.set(seleccionados)

            estado = "creado" if creado else "actualizado"
            self.stdout.write(
                self.style.SUCCESS(
                    f"Grupo '{nombre_grupo}' {estado} con {len(seleccionados)} permisos."
                )
            )