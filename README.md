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
│       └── routers/
├── frontend/             # HTML + CSS + JS
│   ├── index.html
│   ├── style.css
│   ├── app.js
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

## Levantar el proyecto localmente

```bash
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

La API quedará disponible en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.

## Ejecutar pruebas y linter localmente

```bash
pytest
flake8 .
pytest --cov=backend tests/
```

## Levantar el frontend localmente

Basta con abrir `frontend/index.html` en el navegador (o servirlo con cualquier servidor estático), con el backend corriendo en paralelo.

## Base de datos

Ver `database/schema.sql` para el esquema y `database/seed.sql` para datos de ejemplo. Instrucciones detalladas de conexión, a completar por el encargado de BD.
