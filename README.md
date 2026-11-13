# Sistema de Préstamos/Biblioteca — Proyecto Habilidades DevOps

Proyecto académico para la materia de Habilidades DevOps. Stack: Python (FastAPI) + HTML/CSS/JS + MySQL, con pipeline de CI en GitHub Actions.

> Para la guía completa de configuración del entorno, ver [`ONBOARDING.md`](./ONBOARDING.md).
> Para el detalle y justificación de cada herramienta, ver [`herramientas-devops.md`](./herramientas-devops.md).

## Integrantes y roles

| Rol | Responsable | Carpeta principal |
|---|---|---|
| Backend (API REST) | Luis | `backend/` |
| Frontend | _(pendiente)_ | `frontend/` |
| Base de Datos | _(pendiente)_ | `database/` |
| DevOps / CI | _(pendiente)_ | `.github/workflows/` |

## Estructura del repositorio

```
.
├── backend/             # API REST (FastAPI)
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── dependencias.py   # conexión por petición y control de acceso por rol
│       ├── seguridad.py      # contraseñas y tokens de sesión
│       └── routers/          # un archivo por recurso; portal.py = vista del cliente
├── frontend/             # HTML + CSS + JS
│   ├── index.html
│   ├── style.css
│   ├── sesion.js         # sesión, llamadas a la API y escapado de HTML
│   ├── app.js            # panel del personal
│   ├── Login/
│   ├── portal/           # portal de clientes
│   └── pages/
├── database/             # Scripts SQL
│   ├── schema.sql
│   └── seed.sql
├── tests/                # Pruebas automatizadas (pytest)
├── .github/workflows/    # Pipeline de CI
│   └── ci.yml
├── requirements.txt
├── pytest.ini
├── .flake8
├── .gitignore
├── README.md
├── ONBOARDING.md
└── herramientas-devops.md
```

## Cómo trabajar en este repo

1. Clona el repositorio (ver pasos detallados en `ONBOARDING.md`).
2. Crea una rama por feature/tarea: `git checkout -b backend/endpoint-prestamos`.
3. Cada quien trabaja únicamente dentro de su carpeta (`backend/`, `frontend/`, `database/`) para evitar conflictos de merge.
4. Sube tus avances con commits pequeños y descriptivos.
5. Abre un Pull Request hacia `main` — el pipeline de CI corre automáticamente (flake8 + pytest + MySQL).

## Cómo funciona el sistema

Hay dos tipos de cuenta y cada una entra por el mismo login (`frontend/Login/index.html`):

| Perfil | Entra con | Qué puede hacer |
|---|---|---|
| **Cliente** | su correo | Ver sus préstamos y cuántos días le quedan, apartar libros del catálogo (máx. 5 a la vez) y cancelar apartados que no ha recogido. |
| **Bibliotecario / Administrador** | su username | Todo el panel: libros, categorías, clientes, usuarios del personal y préstamos. |

Ciclo de un préstamo:

```
cliente aparta en el portal ──> APARTADO (3 días para recoger) ──(Entregar)──> ACTIVO (14 días)
personal presta en mostrador ───────────────────────────────────────────────> ACTIVO
ACTIVO ──(Devolver)──> DEVUELTO          ACTIVO con la fecha límite vencida se muestra como VENCIDO
```

Mientras un préstamo está APARTADO o ACTIVO, sus libros aparecen como no disponibles.
Un cliente con préstamos vencidos no puede apartar más libros.

La API exige sesión: `POST /login` devuelve un `token` que el frontend manda en el header
`Authorization: Bearer <token>`. Los endpoints del personal responden 403 a los clientes, y los
clientes solo ven sus propios préstamos (`/mi/...`).

## Levantar el proyecto localmente (Windows)

Usa **Python 3.12** (con 3.14 algunas dependencias no instalan). Desde la carpeta del proyecto:

```bash
py -3.12 -m venv venv
venv\Scripts\python -m pip install -r requirements.txt
```

### Base de datos

Crea la base de datos y carga el esquema y los datos de ejemplo (cada comando pide la contraseña de
root de MySQL). `schema.sql` borra y vuelve a crear las tablas, así que puedes repetir estos pasos
para dejar la BD como nueva:

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS biblioteca_db"
mysql -u root -p biblioteca_db -e "source database/schema.sql"
mysql -u root -p biblioteca_db -e "source database/seed.sql"
```

Copia `.env.example` a `.env` y pon tu contraseña de MySQL en `DB_PASSWORD` y un texto secreto en
`SECRET_KEY`.

### Backend y frontend

```bash
venv\Scripts\python -m uvicorn backend.app.main:app --reload
```

La API queda en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`
(usa `POST /login` y luego el botón **Authorize** con el token).

En otra terminal, sirve el frontend y abre `http://localhost:5500/Login/index.html`:

```bash
venv\Scripts\python -m http.server 5500 -d frontend
```

### Cuentas de prueba (de `seed.sql`, solo para desarrollo)

| Perfil | Usuario | Contraseña |
|---|---|---|
| Cliente (tiene un préstamo activo y un apartado) | `ana@example.com` | `cliente123` |
| Cliente (tiene un préstamo vencido) | `luis@example.com` | `cliente123` |
| Bibliotecario | `biblio_db` | `biblio123` |
| Administrador | `admin_db` | `admin123` |

## Ejecutar pruebas y linter localmente

Las pruebas de integración usan la base de datos del `.env`, con `schema.sql` + `seed.sql` cargados.
Dejan los datos como estaban al terminar.

```bash
venv\Scripts\python -m flake8 .
venv\Scripts\python -m pytest --cov=backend tests/
```
