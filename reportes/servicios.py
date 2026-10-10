from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone

from catalogo.models import Libro
from prestamos.models import Prestamo


def prestamos_vencidos(fecha=None):
    """Préstamos sin devolver cuya fecha límite ya pasó."""
    fecha = fecha or timezone.localdate()
    return (
        Prestamo.objects.filter(
            fecha_devolucion__isnull=True,
            fecha_limite__lt=fecha,
        )
        .select_related("libro", "usuario")
        .order_by("fecha_limite")
    )


def libros_mas_prestados(limite=5):
    """Los libros con más préstamos, de mayor a menor."""
    return (
        Libro.objects.annotate(total_prestamos=Count("prestamos"))
        .filter(total_prestamos__gt=0)
        .select_related("autor")
        .order_by("-total_prestamos", "titulo")[:limite]
    )


def resumen_general(fecha=None):
    """Cifras principales de la biblioteca."""
    fecha = fecha or timezone.localdate()
    total_multas = Prestamo.objects.aggregate(total=Sum("multa"))["total"]
    return {
        "total_libros": Libro.objects.count(),
        "prestamos_activos": Prestamo.objects.filter(
            fecha_devolucion__isnull=True
        ).count(),
        "prestamos_vencidos": prestamos_vencidos(fecha).count(),
        "total_multas": total_multas or Decimal("0.00"),
    }