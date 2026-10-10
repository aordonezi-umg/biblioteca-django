import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command


@pytest.mark.django_db
def test_crear_roles_crea_los_dos_grupos():
    # Act
    call_command("crear_roles")
    # Assert
    assert Group.objects.filter(name="Bibliotecario").exists()
    assert Group.objects.filter(name="Estudiante").exists()


@pytest.mark.django_db
def test_crear_roles_se_puede_ejecutar_dos_veces_sin_duplicar():
    call_command("crear_roles")
    call_command("crear_roles")
    assert Group.objects.count() == 2


@pytest.mark.django_db
def test_bibliotecario_gestiona_todo_y_estudiante_solo_puede_ver(django_user_model):
    # Arrange
    call_command("crear_roles")
    bibliotecario = django_user_model.objects.create_user(
        username="biblio", password="clave-de-prueba-123"
    )
    bibliotecario.groups.add(Group.objects.get(name="Bibliotecario"))

    estudiante = django_user_model.objects.create_user(
        username="alumno", password="clave-de-prueba-123"
    )
    estudiante.groups.add(Group.objects.get(name="Estudiante"))

    # Act + Assert: el bibliotecario puede gestionar
    assert bibliotecario.has_perm("prestamos.add_prestamo")
    assert bibliotecario.has_perm("catalogo.delete_libro")

    # El estudiante solo puede ver
    assert estudiante.has_perm("catalogo.view_libro")
    assert estudiante.has_perm("prestamos.view_prestamo")
    assert not estudiante.has_perm("prestamos.add_prestamo")
    assert not estudiante.has_perm("catalogo.delete_libro")