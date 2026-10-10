# 📚 Sistema de Biblioteca Escolar

Plataforma web para gestionar el catálogo de libros, los préstamos, las devoluciones y las multas de una biblioteca escolar.

Proyecto académico desarrollado con **Python** y **Django**.

---

## Módulos

| # | Módulo | App de Django | Descripción |
|---|---|---|---|
| 1 | Usuarios y roles | *(incluida en Django)* + `crear_roles` | Inicio de sesión y roles Bibliotecario y Estudiante |
| 2 | Autores y categorías | `catalogo` | Registro de autores y categorías |
| 3 | Libros | `catalogo` | Catálogo de libros con ISBN y número de ejemplares |
| 4 | Préstamos | `prestamos` | Registro de qué usuario se lleva qué libro |
| 5 | Devoluciones y multas | `prestamos` | Registro de devoluciones y cálculo automático de multas |

### Relaciones entre módulos

```
Autor ─────┐
           ├──► Libro ──┐
Categoría ─┘            ├──► Préstamo (devolución y multa)
Usuario ────────────────┘
```

---

## Reglas de negocio

1. No se puede prestar un libro si todos sus ejemplares ya están prestados.
2. La fecha límite de devolución es, por defecto, 7 días después del préstamo.
3. Multa de **Q5.00 por cada día de retraso**. Se calcula automáticamente.
4. La fecha de devolución no puede ser anterior a la fecha de préstamo.
5. No se puede borrar un autor o una categoría que tenga libros asociados.
6. No se pueden registrar dos libros con el mismo ISBN.

Los valores de las reglas 2 y 3 están en `prestamos/models.py`:

```python
DIAS_PRESTAMO = 7
MULTA_POR_DIA = Decimal("5.00")
```

---

## Roles y permisos

| Rol | Permisos |
|---|---|
| **Superusuario** | Todo, incluida la gestión de usuarios y grupos |
| **Bibliotecario** | Ver, añadir, modificar y borrar libros, autores, categorías y préstamos |
| **Estudiante** | Solo ver libros, autores, categorías y préstamos |

Para que un usuario entre al panel debe tener marcada la casilla **"Es staff"** y pertenecer a un grupo.

---

## Tecnologías

- Python 3.13
- Django 6.1
- SQLite (base de datos)
- pytest y pytest-django (pruebas automatizadas)
- Git y GitHub (control de versiones)

---

## Instalación en una computadora nueva (Windows)

Requisitos: tener instalados **Python 3.10 o superior** y **Git**.

Todos los comandos se ejecutan en PowerShell o en la terminal de VS Code.

```powershell
# 1. Descargar el proyecto
git clone https://github.com/aordonezi-umg/biblioteca-django.git
cd biblioteca-django

# 2. Crear y activar el entorno virtual
py -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Instalar las librerías
python -m pip install -r requirements.txt

# 4. Crear las tablas de la base de datos
python manage.py migrate

# 5. Crear los roles Bibliotecario y Estudiante
python manage.py crear_roles

# 6. Crear el usuario administrador
python manage.py createsuperuser

# 7. Encender el servidor
python manage.py runserver
```

Luego se abre en el navegador: **http://127.0.0.1:8000/admin**

> Si al activar el entorno aparece *"la ejecución de scripts está deshabilitada"*, se ejecuta una vez:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

> La base de datos (`db.sqlite3`) no se sube a GitHub. En una computadora nueva empieza vacía.

---

## Uso diario

```powershell
cd C:\proyectos\biblioteca
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

- Para apagar el servidor: **Ctrl + C** en la terminal.
- Cada terminal nueva necesita activar el entorno; la señal es ver `(venv)` al inicio de la línea.

---

## Pruebas automatizadas

```powershell
pytest -v
```

Resultado esperado: **15 passed**.

| Archivo | Tipo | Qué prueba |
|---|---|---|
| `catalogo/tests.py` | Unitarias e integración | Formato del libro, ISBN único, protección al borrar autores |
| `prestamos/tests.py` | Unitarias e integración | Cálculo de multas, disponibilidad de ejemplares, validación de fechas |
| `prestamos/test_roles.py` | Integración | Creación de grupos y permisos de cada rol |

- **Pruebas unitarias:** revisan una sola función sin base de datos.
- **Pruebas de integración:** revisan varias partes juntas con una base de datos temporal. Los datos reales no se modifican.

---

## Cómo modificar el proyecto

### Agregar un campo a una tabla

1. Editar el modelo en `models.py` de la app correspondiente.
2. Crear y aplicar la migración:
```powershell
   python manage.py makemigrations
   python manage.py migrate
```
3. Si debe verse en la lista del panel, agregarlo a `list_display` en `admin.py`.
4. Ejecutar `pytest -v` para comprobar que nada se rompió.
5. Guardar en Git:
```powershell
   git add .
   git commit -m "Descripción del cambio"
   git push
```

### Agregar un módulo nuevo

1. `python manage.py startapp nombre_modulo`
2. Agregar `'nombre_modulo',` en `INSTALLED_APPS` de `config/settings.py`.
3. Crear los modelos en `nombre_modulo/models.py`.
4. Registrarlos en `nombre_modulo/admin.py`.
5. `python manage.py makemigrations` y `python manage.py migrate`.
6. Escribir pruebas en `nombre_modulo/tests.py` y ejecutar `pytest -v`.

---

## Estructura del proyecto

```
biblioteca/
├── config/                 # Configuración general (settings.py, urls.py)
├── catalogo/               # Módulos 2 y 3: autores, categorías y libros
│   ├── models.py
│   ├── admin.py
│   └── tests.py
├── prestamos/              # Módulos 4 y 5: préstamos, devoluciones y multas
│   ├── management/commands/crear_roles.py   # Módulo 1: roles
│   ├── models.py
│   ├── admin.py
│   ├── tests.py
│   └── test_roles.py
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Limitaciones conocidas y mejoras futuras

- Un estudiante puede ver **todos** los préstamos, no solo los suyos. Requiere pantallas propias fuera del panel de administración.
- La interfaz usa el panel de administración de Django; no hay pantallas públicas personalizadas.
- Falta el módulo de **Reportes** (préstamos vencidos y libros más prestados).
- No hay pruebas de extremo a extremo (simulación de un usuario en el navegador).