from django.contrib import admin
from django.utils import timezone

from .models import Prestamo


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = (
        "libro",
        "usuario",
        "fecha_prestamo",
        "fecha_limite",
        "fecha_devolucion",
        "estado",
        "multa",
    )
    search_fields = ("libro__titulo", "usuario__username")
    list_filter = ("fecha_prestamo",)
    readonly_fields = ("multa",)
    actions = ["marcar_como_devuelto"]

    @admin.display(description="estado")
    def estado(self, obj):
        if obj.devuelto:
            return "Devuelto"
        if obj.fecha_limite < timezone.localdate():
            return "Vencido"
        return "Activo"

    @admin.action(description="Marcar como devueltos (fecha de hoy)")
    def marcar_como_devuelto(self, request, queryset):
        cantidad = 0
        for prestamo in queryset.filter(fecha_devolucion__isnull=True):
            prestamo.marcar_devuelto()
            cantidad += 1
        self.message_user(request, f"{cantidad} préstamo(s) marcados como devueltos.")