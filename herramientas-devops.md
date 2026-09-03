# Herramientas DevOps — Proyecto | Habilidades DevOps

**Materia:** Habilidades DevOps
**Stack del sistema:** Python (backend REST API) + Frontend (HTML/CSS/JavaScript) + MySQL
**Contexto:** Proyecto

---

## 1. Python (Backend)

**Versión recomendada:** Python 3.14.0 (estable y con amplio soporte de librerías)

**Función:** Lenguaje del backend — expone una API REST mediante **FastAPI** o **Flask**.

**Por qué la usamos:** Es el stack ya definido para el proyecto; fijar una versión concreta es lo que hace reproducible el entorno de CI.

**Importante:** Python se ejecuta en el servidor y NO se envía al navegador del cliente.

## 2. Framework Backend — FastAPI o Flask

**FastAPI — Recomendado**
- **Versión recomendada:** FastAPI ≥ 0.100.0
- **Función:** Expone endpoints REST (`/prestamos`, `/libros`, etc.) que el frontend consume vía fetch().
- **Ventajas académicas:**
  - Documentación automática interactiva (Swagger/OpenAPI) en `/docs`
  - Validación automática de datos con Pydantic
  - Muy moderna y valorada en evaluaciones
  - Fácil de testear y documentar

**Flask — Alternativa**
- **Versión recomendada:** Flask ≥ 2.3.0
- **Función:** Expone endpoints REST de manera más minimalista
- **Ventajas académicas:**
  - Más ligero y simple de entender
  - Ampliamente conocido

```python
# Ejemplo FastAPI
from fastapi import FastAPI

app = FastAPI()

@app.get("/prestamos")
async def obtener_prestamos():
    return {"prestamos": [...]}

@app.get("/libros")
async def obtener_libros():
    return {"libros": [...]}
```

## 3. Frontend — HTML + CSS + JavaScript Puro

**Función:** Interfaz de usuario ejecutada en el navegador del cliente.

**Por qué esta opción:**
- No requiere herramientas adicionales complejas (Node.js, npm, bundlers)
- Más fácil de justificar en una evaluación académica
- Todo el equipo puede entenderlo fácilmente
- Utiliza `fetch()` para consumir la API del backend

```javascript
// Ejemplo: Consumir la API del backend
fetch('http://localhost:8000/prestamos')
  .then(response => response.json())
  .then(data => {
    console.log('Préstamos:', data);
    renderizar(data);
  });
```

**Estructura recomendada del frontend:**
```
frontend/
├── index.html
├── style.css
├── app.js
└── pages/
    ├── prestamos.html
    ├── libros.html
    └── usuarios.html
```

## 4. pytest (Pruebas backend)

**Versión recomendada:** 9.1.1

**Función:** Framework de pruebas automatizadas para Python (backend).

**Por qué la usamos:** Valida que los endpoints del API sigan funcionando conforme el equipo agrega o modifica código. Sin pruebas automáticas, el pipeline de CI solo estaría "ejecutando código sin validar".

```python
# Ejemplo: Prueba de un endpoint
def test_obtener_prestamos():
    response = client.get("/prestamos")
    assert response.status_code == 200
    assert "prestamos" in response.json()
```

**Nota:** Las pruebas del frontend (si las hay) requieren herramientas como Selenium o Playwright, fuera del scope de este proyecto.

## 5. flake8

**Versión recomendada:** 7.3.0

**Función:** Linter de estilo de código para Python (basado en PEP8).

**Por qué la usamos:** Mantiene consistencia de estilo entre los distintos miembros del equipo que trabajan en el mismo backend. Se integra como un paso más del pipeline de CI.

## 6. venv + requirements.txt

**Versión recomendada:** `venv` viene incluido con Python 3.13+. `pip` ≥ 24.x (se actualiza junto con Python).

**Función:** Entorno virtual de Python y archivo de dependencias fijas.

**Por qué la usamos:** Garantiza que el proyecto sea reproducible — cualquier miembro del equipo (o quien lo evalúe) puede levantar exactamente el mismo entorno con `pip install -r requirements.txt`.

**Ejemplo de requirements.txt para FastAPI:**
```text
fastapi==0.104.1
uvicorn==0.24.0
pytest==9.1.1
flake8==7.3.0
pytest-cov==4.0.0
mysql-connector-python==8.2.0
```

## 7. MySQL 

**Versión recomendada:** MySQL 8.0.46 LTS 

**Función:** Sistema de gestión de base de datos relacional — almacena datos consumidos por el API.

**Por qué la usamos:** Es la base de datos ya definida para el sistema. Para las pruebas automáticas, GitHub Actions puede levantar una instancia de MySQL como *service container* dentro del propio workflow.

## 8. Coverage (`pytest-cov`) — *opcional*

**Versión recomendada:** la más reciente publicada en marzo de 2026

**Función:** Mide el porcentaje de código cubierto por las pruebas automatizadas (solo backend).

**Por qué la usamos:** Es un complemento sencillo que agrega valor al pipeline de CI, mostrando qué tan probado está el backend.

---

## Flujo general — Backend + Frontend

```
Git / GitHub  (código y documentación del proyecto)
      │
      ├─ Backend (Python + FastAPI/Flask)
      │         │
      │         ▼
      │   GitHub Actions (CI)
      │         ├─ venv + requirements.txt   → entorno reproducible
      │         ├─ flake8                    → calidad de código
      │         ├─ pytest + MySQL            → pruebas automatizadas
      │         └─ coverage (opcional)       → métricas de cobertura
      │
      └─ Frontend (HTML + CSS + JavaScript)
                 │
                 └─ Consumir API en http://localhost:8000
```

## Cliente consumiendo el API

```text
Browser (Frontend)
    │
    ├─ fetch('http://localhost:8000/prestamos')
    │
    ▼
Backend API (FastAPI/Flask)
    │
    ├─ Valida datos
    ├─ Consulta MySQL
    │
    ▼
Response JSON
    │
    ▼
Browser renderiza
```
