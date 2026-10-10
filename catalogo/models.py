from django.db import models


class Autor(models.Model):
    """Tabla de autores de los libros."""

    nombre = models.CharField("nombre", max_length=150)
    nacionalidad = models.CharField("nacionalidad", max_length=100, blank=True)

    class Meta:
        verbose_name = "autor"
        verbose_name_plural = "autores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    """Tabla de categorías o géneros (Novela, Ciencia, Historia...)."""

    nombre = models.CharField("nombre", max_length=100, unique=True)
    descripcion = models.TextField("descripción", blank=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    """Tabla de libros del catálogo. Cada libro tiene un autor y una categoría."""

    titulo = models.CharField("título", max_length=200)
    isbn = models.CharField("ISBN", max_length=13, unique=True)
    autor = models.ForeignKey(
        Autor,
        on_delete=models.PROTECT,
        related_name="libros",
        verbose_name="autor",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="libros",
        verbose_name="categoría",
    )
    anio_publicacion = models.PositiveIntegerField(
        "año de publicación", null=True, blank=True
    )
    ejemplares = models.PositiveIntegerField("ejemplares", default=1)

    class Meta:
        verbose_name = "libro"
        verbose_name_plural = "libros"
        ordering = ["titulo"]

    def __str__(self):
        return f"{self.titulo} ({self.autor})"