import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError

from catalogo.models import Autor, Categoria, Libro


@pytest.fixture
def autor(db):
    return Autor.objects.create(nombre="Autor de prueba")


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre="Novela")


# ---------- Prueba unitaria ----------

def test_libro_se_muestra_con_titulo_y_autor():
    # Arrange
    libro = Libro(titulo="Cien años de soledad", autor=Autor(nombre="García Márquez"))
    # Act
    texto = str(libro)
    # Assert
    assert texto == "Cien años de soledad (García Márquez)"


# ---------- Pruebas de integración ----------

@pytest.mark.django_db
def test_no_permite_dos_libros_con_el_mismo_isbn(autor, categoria):
    Libro.objects.create(
        titulo="Libro A", isbn="1111111111111", autor=autor, categoria=categoria
    )
    with pytest.raises(IntegrityError):
        Libro.objects.create(
            titulo="Libro B", isbn="1111111111111", autor=autor, categoria=categoria
        )


@pytest.mark.django_db
def test_no_permite_borrar_un_autor_que_tiene_libros(autor, categoria):
    Libro.objects.create(
        titulo="Libro A", isbn="2222222222222", autor=autor, categoria=categoria
    )
    with pytest.raises(ProtectedError):
        autor.delete()