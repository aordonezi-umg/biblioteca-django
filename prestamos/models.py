from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from catalogo.models import Libro

# Reglas de negocio en un solo lugar, para cambiarlas fácilmente
DIAS_PRESTAMO = 7
MULTA_POR_DIA = Decimal("5.00")
MULTA_MAXIMA = Decimal("100.00")


def fecha_limite_por_defecto():
    """Fecha de hoy + 7 días."""
    return timezone.localdate() + timedelta(days=DIAS_PRESTAMO)


class Prestamo(models.Model):
    """Registra qué usuario se llevó qué libro, cuándo debe devolverlo y su multa."""

    libro = models.ForeignKey(
        Libro,
        on_delete=models.PROTECT,
        related_name="prestamos",
        verbose_name="libro",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="prestamos",
        verbose_name="usuario",
    )
    fecha_prestamo = models.DateField("fecha de préstamo", default=timezone.localdate)
    fecha_limite = models.DateField("fecha límite", default=fecha_limite_por_defecto)
    fecha_devolucion = models.DateField("fecha de devolución", null=True, blank=True)
    multa = models.DecimalField(
        "multa (Q)",
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
    )

    class Meta:
        verbose_name = "préstamo"
        verbose_name_plural = "préstamos"
        ordering = ["-fecha_prestamo"]

    def __str__(self):
        return f"{self.libro.titulo} → {self.usuario}"

    @property
    def devuelto(self):
        """True si el libro ya fue devuelto."""
        return self.fecha_devolucion is not None

    def calcular_multa(self, fecha_referencia=None):
        """Q5.00 por cada día de retraso después de la fecha límite."""
        fecha = fecha_referencia or self.fecha_devolucion or timezone.localdate()
        dias_retraso = (fecha - self.fecha_limite).days
        if dias_retraso <= 0:
            return Decimal("0.00")
        return min(MULTA_POR_DIA * dias_retraso, MULTA_MAXIMA)

    def clean(self):
        """Validaciones de reglas de negocio antes de guardar."""
        errores = {}

        if self.fecha_prestamo and self.fecha_limite:
            if self.fecha_limite < self.fecha_prestamo:
                errores["fecha_limite"] = (
                    "La fecha límite no puede ser anterior a la fecha de préstamo."
                )

        if self.fecha_prestamo and self.fecha_devolucion:
            if self.fecha_devolucion < self.fecha_prestamo:
                errores["fecha_devolucion"] = (
                    "La fecha de devolución no puede ser anterior a la fecha de préstamo."
                )

        if self.libro_id and not self.devuelto:
            prestamos_activos = (
                Prestamo.objects.filter(
                    libro_id=self.libro_id, fecha_devolucion__isnull=True
                )
                .exclude(pk=self.pk)
                .count()
            )
            if prestamos_activos >= self.libro.ejemplares:
                errores["libro"] = (
                    "No hay ejemplares disponibles de este libro: "
                    "todos están prestados."
                )

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        """Calcula la multa automáticamente al guardar."""
        if self.devuelto:
            self.multa = self.calcular_multa()
        else:
            self.multa = Decimal("0.00")
        super().save(*args, **kwargs)

    def marcar_devuelto(self, fecha=None):
        """Registra la devolución (hoy, si no se indica otra fecha)."""
        self.fecha_devolucion = fecha or timezone.localdate()
        self.save()