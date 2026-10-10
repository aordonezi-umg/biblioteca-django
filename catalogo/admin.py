from django.contrib import admin

from .models import Autor, Categoria, Libro


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nacionalidad")
    search_fields = ("nombre",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "categoria", "isbn", "ejemplares")
    list_filter = ("categoria",)
    search_fields = ("titulo", "isbn", "autor__nombre")