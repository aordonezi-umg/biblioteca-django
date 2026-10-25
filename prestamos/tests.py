from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from catalogo.models import Autor, Categoria, Libro
from prestamos.models import Prestamo


# ============================================================
# FIXTURES: datos de prueba reutilizables
# ============================================================

@pytest.fixture
def libro(db):
    """Un libro con 2 ejemplares, con su autor y su categoría."""
    autor = Autor.objects.create(nombre="Autor de prueba")
    categoria = Categoria.objects.create(nombre="Categoría de prueba")
    return Libro.objects.create(
        titulo="Libro de prueba",
        isbn="1234567890123",
        autor=autor,
        categoria=categoria,
        ejemplares=2,
    )


@pytest.fixture
def usuario(django_user_model):
    """Un usuario estudiante."""
    return django_user_model.objects.create_user(
        username="estudiante", password="clave-de-prueba-123"
    )


# ============================================================
# PRUEBAS UNITARIAS: calcular_multa() sin base de datos
# ============================================================

def test_multa_es_cero_si_se_devuelve_el_dia_limite():
    # Arrange (preparar)
    prestamo = Prestamo(
        fecha_prestamo=date(2026, 10, 1),
        fecha_limite=date(2026, 10, 8),
        fecha_devolucion=date(2026, 10, 8),
    )
    # Act (actuar)
    multa = prestamo.calcular_multa()
    # Assert (verificar)
    assert multa == Decimal("0.00")


def test_multa_es_cero_si_se_devuelve_antes_del_limite():
    prestamo = Prestamo(
        fecha_prestamo=date(2026, 10, 1),
        fecha_limite=date(2026, 10, 8),
        fecha_devolucion=date(2026, 10, 3),
    )
    assert prestamo.calcular_multa() == Decimal("0.00")


def test_multa_cobra_5_quetzales_por_cada_dia_de_retraso():
    prestamo = Prestamo(
        fecha_prestamo=date(2026, 10, 1),
        fecha_limite=date(2026, 10, 5),
        fecha_devolucion=date(2026, 10, 9),
    )
    assert prestamo.calcular_multa() == Decimal("20.00")


def test_prestamo_sin_fecha_de_devolucion_no_esta_devuelto():
    prestamo = Prestamo(fecha_devolucion=None)
    assert prestamo.devuelto is False


# ============================================================
# PRUEBAS DE INTEGRACIÓN: modelo + reglas + base de datos
# ============================================================

@pytest.mark.django_db
def test_permite_prestar_si_hay_ejemplares_disponibles(libro, usuario):
    # Arrange
    prestamo = Prestamo(libro=libro, usuario=usuario)
    # Act
    prestamo.full_clean()  # ejecuta las validaciones; no debe lanzar error
    prestamo.save()
    # Assert
    assert Prestamo.objects.count() == 1


@pytest.mark.django_db
def test_bloquea_prestamo_si_todos_los_ejemplares_estan_prestados(libro, usuario):
    # Arrange: se prestan los 2 ejemplares
    Prestamo.objects.create(libro=libro, usuario=usuario)
    Prestamo.objects.create(libro=libro, usuario=usuario)
    tercero = Prestamo(libro=libro, usuario=usuario)
    # Act + Assert: el tercero debe ser rechazado en el campo "libro"
    with pytest.raises(ValidationError) as error:
        tercero.full_clean()
    assert "libro" in error.value.message_dict


@pytest.mark.django_db
def test_devolver_un_libro_libera_un_ejemplar(libro, usuario):
    # Arrange
    primero = Prestamo.objects.create(libro=libro, usuario=usuario)
    Prestamo.objects.create(libro=libro, usuario=usuario)
    # Act
    primero.marcar_devuelto()
    nuevo = Prestamo(libro=libro, usuario=usuario)
    # Assert: ahora sí se permite (no lanza error)
    nuevo.full_clean()


@pytest.mark.django_db
def test_devolucion_con_retraso_guarda_la_multa_en_la_base_de_datos(libro, usuario):
    # Arrange
    prestamo = Prestamo.objects.create(
        libro=libro,
        usuario=usuario,
        fecha_prestamo=date(2026, 10, 1),
        fecha_limite=date(2026, 10, 5),
    )
    # Act
    prestamo.marcar_devuelto(fecha=date(2026, 10, 9))
    prestamo.refresh_from_db()  # vuelve a leerlo desde la base de datos
    # Assert
    assert prestamo.multa == Decimal("20.00")
    assert prestamo.devuelto is True


@pytest.mark.django_db
def test_rechaza_devolucion_anterior_a_la_fecha_de_prestamo(libro, usuario):
    prestamo = Prestamo(
        libro=libro,
        usuario=usuario,
        fecha_prestamo=date(2026, 10, 5),
        fecha_limite=date(2026, 10, 12),
        fecha_devolucion=date(2026, 10, 1),
    )
    with pytest.raises(ValidationError) as error:
        prestamo.full_clean()
    assert "fecha_devolucion" in error.value.message_dict
    

def test_multa_no_supera_el_tope_maximo():
    # 55 días de retraso x Q5 = Q275, pero el tope es Q100
    prestamo = Prestamo(
        fecha_prestamo=date(2026, 9, 1),
        fecha_limite=date(2026, 9, 5),
        fecha_devolucion=date(2026, 10, 30),
    )
    assert prestamo.calcular_multa() == Decimal("100.00")