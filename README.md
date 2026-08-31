# DevOps — Proyecto Habilidades DevOps

Repositorio del proyecto de la materia **Habilidades DevOps**: una aplicación para la gestión de préstamos en una biblioteca desarrollada en Python y respaldada por MySQL.
## ¿Qué es este proyecto?

Este proyecto es una aplicación para la gestión de una biblioteca. Su objetivo principal es facilitar el control del inventario de libros y el proceso de préstamos y devoluciones. Además, permite registrar nuevos empleados y administradores, asegurando que la biblioteca funcione de manera organizada y eficiente.
## ¿Para qué nos sirve?
**Gestión de inventario:** Saber qué libros están disponibles, cuáles están prestados y cuáles han sido devueltos.

**Control de préstamos:** Registrar fácilmente quién pidió un libro y cuándo debe devolverlo.

**Administración de usuarios:** Dar de alta a nuevos empleados y administradores con sus respectivos roles.

---
## Ventajas
**Organización:** Todo el inventario y los préstamos quedan registrados en un solo sistema.

**Rapidez:** Los procesos de préstamo y devolución se realizan en segundos.

**Seguridad:** Los datos se almacenan en una base de datos confiable (MySQL), evitando pérdidas de información.

**Escalabilidad:** Se puede ampliar para incluir nuevas funciones, como reportes o estadísticas.

**Accesibilidad:** Al estar desarrollado en Python, es fácil de mantener y mejorar por estudiantes o profesionales.

---
## Resumen

- Stack: Python (backend / frontend) + MySQL
- Objetivo: Facilitar los préstamos de libros, registrar entregas y devoluciones y administrar el inventario de la biblioteca.
- Propósito: almacenar el código fuente, las pruebas y la configuración de CI/CD para la asignatura.

---

## Requisitos

- Python 3.14.0 (recomendado)
- MySQL 8.0.x (sugerido: 8.0.46)
- Git
- Cuenta de GitHub
- Editor de código (recomendado: Visual Studio Code)

Comprobar versiones:

```bash
python --version
# Ejemplo: Python 3.14.0

git --version
```

---

## Estructura del proyecto (recomendada)

```text
proyecto/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── backend/
├── frontend/
├── tests/
├── requirements.txt
├── README.md
└── .gitignore
```

La estructura puede variar según la implementación final.

---

## Instalación y puesta en marcha (local)

1. Clonar el repositorio:

```bash
git clone URL_DEL_REPOSITORIO
cd NOMBRE_DEL_PROYECTO
```

2. Crear y activar el entorno virtual

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Configurar la base de datos MySQL:

- Crear la base de datos (por ejemplo `biblioteca_db`).
- Configurar usuario y contraseña.
- Definir las variables de entorno que use la aplicación (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`).

5. Ejecutar la aplicación (los comandos pueden variar según la estructura del proyecto):

```bash
# ejemplo genérico (ajustar según la implementación)
python -m backend.app
```

---

## Pruebas y calidad de código

- Ejecutar tests con pytest:

```bash
pytest
```

- Ejecutar coverage:

```bash
pytest --cov=.
```

- Ejecutar flake8 (lint):

```bash
flake8 .
```

Se recomienda ejecutar estas comprobaciones antes de subir cambios.

---

## Integración continua (GitHub Actions)

El proyecto incluye (o puede incluir) un pipeline de CI en GitHub Actions con el siguiente flujo:

1. Preparar entorno Python
2. Instalar dependencias
3. Ejecutar flake8
4. Levantar servicio MySQL para pruebas
5. Ejecutar pytest
6. Generar reporte de coverage (opcional)

Ejemplo de servicio MySQL en GitHub Actions:

```yaml
services:
  mysql:
    image: mysql:8.0
    env:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: test_db
    ports:
      - 3306:3306
    options: >-
      --health-cmd "mysqladmin ping --silent"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 3
```

---

## Buenas prácticas del equipo

* No subir la carpeta `venv/` al repositorio.
* Mantener `requirements.txt` actualizado.
* Crear pruebas para nuevas funcionalidades.
* Ejecutar `pytest` y `flake8` antes de push.
* Usar mensajes de commit claros y descriptivos.
* No almacenar contraseñas ni credenciales en el código; usar variables de entorno o un gestor de secretos.
* Verificar que el pipeline de CI finalice correctamente antes de mergear.

---

## .gitignore recomendado

```text
venv/
__pycache__/
*.pyc
.env
.pytest_cache/
.coverage
htmlcov/
```

---

## Checklist de onboarding

* [ ] Tiene Python instalado.
* [ ] Tiene Git instalado.
* [ ] Tiene acceso al repositorio de GitHub.
* [ ] Clonó correctamente el proyecto.
* [ ] Creó y activó el entorno virtual.
* [ ] Instaló `requirements.txt`.
* [ ] Puede ejecutar `pytest`.
* [ ] Puede ejecutar `flake8`.
* [ ] Puede conectarse a la base de datos de desarrollo, si corresponde.
* [ ] Comprende la estructura básica del proyecto.
* [ ] Comprende el flujo Git → GitHub → GitHub Actions.
* [ ] Realizó correctamente un commit y push.
* [ ] El pipeline de CI termina correctamente.

---

## Contribuir

1. Crear una rama para su cambio:

```bash
git checkout -b feat/mi-cambio
```

2. Asegurarse de que `flake8` y `pytest` pasen localmente.
3. Abrir un Pull Request describiendo los cambios.
