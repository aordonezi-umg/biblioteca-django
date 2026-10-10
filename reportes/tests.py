from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse

from catalogo.models import Autor, Categoria, Libro
from prestamos.models import Prestamo
from reportes import servicios

# Fecha fija para que las pruebas den siempre el mismo resultado
HOY = date(2026, 10, 9)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def libros(db):
    autor = Autor.objects.create(nombre="Autor de prueba")
    categoria = Categoria.objects.create(nombre="Categoría de prueba")
    libro_a = Libro.objects.create(
        titulo="Libro A", isbn="1000000000001",
        autor=autor, categoria=categoria, ejemplares=5,
    )
    libro_b = Libro.objects.create(
        titulo="Libro B", isbn="1000000000002",
        autor=autor, categoria=categoria, ejemplares=5,
    )
    return libro_a, libro_b


@pytest.fixture
def usuario(django_user_model):
    return django_user_model.objects.create_user(
        username="lector", password="clave-de-prueba-123"
    )


def crear_usuario_con_rol(django_user_model, username, rol):
    """Crea un usuario staff y lo agrega al grupo indicado."""
    call_command("crear_roles")
    usuario = django_user_model.objects.create_user(
        username=username, password="clave-de-prueba-123", is_staff=True
    )
    usuario.groups.add(Group.objects.get(name=rol))
    return usuario


# ============================================================
# PRUEBAS DE INTEGRACIÓN: servicios + base de datos
# ============================================================

@pytest.mark.django_db
def test_vencidos_incluye_solo_prestamos_activos_con_fecha_limite_pasada(libros, usuario):
    # Arrange
    libro_a, _ = libros
    vencido = Prestamo.objects.create(
        libro=libro_a, usuario=usuario,
        fecha_prestamo=date(2026, 9, 20), fecha_limite=date(2026, 9, 27),
    )
    Prestamo.objects.create(  # todavía a tiempo
        libro=libro_a, usuario=usuario,
        fecha_prestamo=date(2026, 10, 5), fecha_limite=date(2026, 10, 12),
    )
    Prestamo.objects.create(  # vencido pero ya devuelto
        libro=libro_a, usuario=usuario,
        fecha_prestamo=date(2026, 9, 20), fecha_limite=date(2026, 9, 27),
        fecha_devolucion=date(2026, 9, 30),
    )
    # Act
    resultado = list(servicios.prestamos_vencidos(HOY))
    # Assert
    assert resultado == [vencido]


@pytest.mark.django_db
def test_libros_mas_prestados_ordena_de_mayor_a_menor(libros, usuario):
    # Arrange
    libro_a, libro_b = libros
    for _ in range(3):
        Prestamo.objects.create(libro=libro_b, usuario=usuario)
    Prestamo.objects.create(libro=libro_a, usuario=usuario)
    # Act
    resultado = list(servicios.libros_mas_prestados())
    # Assert
    assert [libro.titulo for libro in resultado] == ["Libro B", "Libro A"]
    assert resultado[0].total_prestamos == 3


@pytest.mark.django_db
def test_resumen_general_cuenta_prestamos_y_suma_multas(libros, usuario):
    # Arrange
    libro_a, _ = libros
    Prestamo.objects.create(  # 4 días tarde -> Q20.00
        libro=libro_a, usuario=usuario,
        fecha_prestamo=date(2026, 10, 1), fecha_limite=date(2026, 10, 5),
        fecha_devolucion=date(2026, 10, 9),
    )
    Prestamo.objects.create(  # 2 días tarde -> Q10.00
        libro=libro_a, usuario=usuario,
        fecha_prestamo=date(2026, 10, 1), fecha_limite=date(2026, 10, 5),
        fecha_devolucion=date(2026, 10, 7),
    )
    Prestamo.objects.create(  # activo y a tiempo
        libro=libro_a, usuario=usuario,
        fecha_prestamo=date(2026, 10, 8), fecha_limite=date(2026, 10, 15),
    )
    # Act
    resumen = servicios.resumen_general(HOY)
    # Assert
    assert resumen["total_libros"] == 2
    assert resumen["prestamos_activos"] == 1
    assert resumen["prestamos_vencidos"] == 0
    assert resumen["total_multas"] == Decimal("30.00")


# ============================================================
# PRUEBAS DE INTEGRACIÓN: página web + seguridad
# ============================================================

@pytest.mark.django_db
def test_reportes_redirige_al_login_si_no_hay_sesion(client):
    respuesta = client.get(reverse("reportes:panel"))
    assert respuesta.status_code == 302
    assert "/admin/login/" in respuesta.url


@pytest.mark.django_db
def test_estudiante_no_puede_ver_reportes(client, django_user_model):
    estudiante = crear_usuario_con_rol(django_user_model, "alumno", "Estudiante")
    client.force_login(estudiante)
    respuesta = client.get(reverse("reportes:panel"))
    assert respuesta.status_code == 403


@pytest.mark.django_db
def test_bibliotecario_puede_ver_reportes(client, django_user_model):
    bibliotecario = crear_usuario_con_rol(django_user_model, "biblio", "Bibliotecario")
    client.force_login(bibliotecario)
    respuesta = client.get(reverse("reportes:panel"))
    assert respuesta.status_code == 200
    assert "Préstamos vencidos" in respuesta.content.decode()