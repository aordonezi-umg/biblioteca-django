from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from . import servicios


@require_GET
@staff_member_required
@permission_required("prestamos.change_prestamo", raise_exception=True)
def panel_reportes(request):
    hoy = timezone.localdate()

    vencidos = list(servicios.prestamos_vencidos(hoy))
    for prestamo in vencidos:
        prestamo.dias_retraso = (hoy - prestamo.fecha_limite).days
        prestamo.multa_acumulada = prestamo.calcular_multa(hoy)

    contexto = {
        **admin.site.each_context(request),
        "title": "Reportes de la biblioteca",
        "hoy": hoy,
        "resumen": servicios.resumen_general(hoy),
        "vencidos": vencidos,
        "mas_prestados": servicios.libros_mas_prestados(),
    }
    return render(request, "reportes/panel.html", contexto)