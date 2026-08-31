# Documento de Onboarding del Proyecto

## Habilidades DevOps

**Materia:** Habilidades DevOps
**Stack:** Python + MySQL
**Control de versiones:** Git / GitHub
**Integración continua:** GitHub Actions

---

## 1. Introducción

Bienvenido al proyecto de la materia **Habilidades DevOps**.

El objetivo de este documento es proporcionar a los nuevos integrantes del equipo una guía para preparar su entorno de desarrollo, comprender las herramientas utilizadas y ejecutar correctamente el p[...]

El sistema está desarrollado utilizando **Python** para el frontend y backend, y **MySQL** como sistema de gestión de base de datos.

Además, el proyecto utiliza prácticas de DevOps para automatizar la validación del código mediante **Integración Continua (CI)** con GitHub Actions.

El flujo principal del proyecto es:

**Git / GitHub → GitHub Actions → Entorno virtual → Flake8 → Pytest + MySQL → Coverage**

---

# 2. Arquitectura general del entorno

El proyecto utiliza las siguientes herramientas:

| Herramienta      |Función                          |
| ---------------- | -------------------------------- |
| Python 3.14.0    | Lenguaje principal del proyecto  |
| pytest 9.1.1     | Pruebas automatizadas            |
| flake8 7.3.0     | Análisis y calidad del código    |
| venv             | Creación del entorno virtual     |
| pip              | Administración de dependencias   |
| requirements.txt | Control de dependencias          |
| MySQL 8.0.46 LTS | Base de datos                    |
| pytest-cov       | Medición de cobertura de pruebas |
| Git              | Control de versiones             |
| GitHub           | Repositorio y colaboración       |
| GitHub Actions   | Integración continua             |

---

# 3. Requisitos previos

Antes de comenzar, el integrante debe tener instalado:

* Python 3.14.0
* Git
* Una cuenta de GitHub
* Un editor de código, preferentemente Visual Studio Code
* Acceso al repositorio del proyecto

Para comprobar Python:

```bash
python --version
```

El resultado esperado es similar a:

```text
Python 3.14.0
```

Para comprobar Git:

```bash
git --version
```

---

# 4. Clonar el proyecto

El primer paso es obtener una copia local del repositorio.

Ejecutar:

```bash
git clone URL_DEL_REPOSITORIO
```

Después ingresar al directorio:

```bash
cd NOMBRE_DEL_PROYECTO
```

Se recomienda comprobar que el repositorio se haya descargado correctamente:

```bash
git status
```

---

# 5. Configuración del entorno virtual

El proyecto utiliza **venv** para crear un entorno virtual de Python.

El entorno virtual permite mantener aisladas las dependencias del proyecto y evita conflictos con otros proyectos instalados en la computadora.

## Windows

Ejecutar:

```bash
python -m venv venv
```

Activar el entorno:

```bash
venv\Scripts\activate
```

Cuando el entorno esté activo, la terminal mostrará normalmente:

```text
(venv)
```

## Linux / macOS

Crear el entorno:

```bash
python3 -m venv venv
```

Activarlo:

```bash
source venv/bin/activate
```

---

# 6. Instalación de dependencias

Una vez activado el entorno virtual, instalar las dependencias mediante:

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` contiene las versiones de los paquetes necesarios para ejecutar y validar el proyecto.

Esto permite que todos los integrantes trabajen con un entorno consistente.

Para comprobar las dependencias instaladas:

```bash
pip list
```

---

# 7. Estructura recomendada del proyecto

La estructura puede organizarse de la siguiente manera:

```text
proyecto/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── backend/
│   ├── ...
│   └── ...
│
├── frontend/
│   ├── ...
│   └── ...
│
├── tests/
│   ├── test_*.py
│   └── ...
│
├── requirements.txt
├── README.md
└── .gitignore
```

La estructura puede variar dependiendo de la implementación final del sistema.

---

# 8. Python

**Python** es el lenguaje principal utilizado en el proyecto.

Se utiliza tanto para el desarrollo del sistema como para la ejecución de las pruebas y herramientas de calidad.

### Versión recomendada

**Python 3.14.0**

Fijar una versión concreta ayuda a mantener la reproducibilidad del entorno y reduce problemas derivados de diferencias entre versiones.

---

# 9. pytest

**pytest** es el framework utilizado para realizar las pruebas automatizadas.

### Versión recomendada

**pytest 9.1.1**

Su función dentro del proyecto es verificar automáticamente que las funciones del sistema continúen funcionando correctamente después de realizar cambios.

Por ejemplo:

```bash
pytest
```

Si todas las pruebas son correctas, pytest mostrará un resultado exitoso.

Las pruebas deben almacenarse dentro del directorio:

```text
tests/
```

Ejemplo:

```text
tests/
├── test_login.py
├── test_usuarios.py
└── test_productos.py
```

---

# 10. Flake8

**Flake8** es la herramienta utilizada para realizar análisis estático del código Python.

### Versión recomendada

**flake8 7.3.0**

Su objetivo es detectar problemas relacionados con:

* Estilo de código
* Errores comunes
* Convenciones PEP 8
* Código potencialmente problemático

Para ejecutar Flake8:

```bash
flake8 .
```

Antes de realizar un commit, se recomienda ejecutar esta validación para detectar problemas en el código.

---

# 11. requirements.txt

El archivo:

```text
requirements.txt
```

contiene las dependencias necesarias para ejecutar y probar el proyecto.

Un ejemplo podría ser:

```text
pytest==9.1.1
flake8==7.3.0
pytest-cov==...
```

Las versiones deben mantenerse controladas para garantizar que los diferentes integrantes trabajen con dependencias compatibles.

Para instalar todas las dependencias:

```bash
pip install -r requirements.txt
```

---

# 12. MySQL

**MySQL** es el sistema de gestión de bases de datos utilizado por el proyecto.

### Versión recomendada

**MySQL 8.0.46 LTS**

La base de datos almacena y administra la información utilizada por el sistema.

Para las pruebas automatizadas, el pipeline de GitHub Actions puede utilizar una instancia de MySQL como servicio temporal.

Esto permite ejecutar las pruebas sin depender de una base de datos instalada en la computadora del desarrollador.

---

# 13. Base de datos para pruebas

Dentro del entorno de CI, GitHub Actions puede levantar un servicio MySQL utilizando un contenedor.

Por ejemplo:

```text
mysql:8.4
```

Esto permite que el pipeline tenga acceso a una base de datos independiente para ejecutar las pruebas.

El objetivo es evitar que las pruebas modifiquen la base de datos utilizada durante el desarrollo.

El flujo sería:

```text
GitHub Actions
      │
      ▼
Levanta MySQL
      │
      ▼
Configura la base de datos
      │
      ▼
Ejecuta pytest
      │
      ▼
Obtiene resultado de las pruebas
```

---

# 14. Coverage

**pytest-cov** es una herramienta opcional utilizada para medir la cobertura del código.

La cobertura indica qué porcentaje del código fue ejecutado durante las pruebas automatizadas.

Por ejemplo:

```text
TOTAL    85%
```

Esto significa que aproximadamente el 85 % de las líneas analizadas fueron ejecutadas durante las pruebas.

Para ejecutar pytest con cobertura:

```bash
pytest --cov=.
```

También se puede generar un reporte HTML:

```bash
pytest --cov=. --cov-report=html
```

Esto permite consultar visualmente qué partes del código están cubiertas y cuáles necesitan más pruebas.

---

# 15. Git y GitHub

Git se utiliza para controlar las diferentes versiones del código.

GitHub funciona como repositorio central del proyecto y permite la colaboración entre los integrantes del equipo.

Flujo básico de trabajo:

```text
Modificar código
      ↓
git add
      ↓
git commit
      ↓
git push
      ↓
GitHub
      ↓
GitHub Actions
```

Comandos principales:

```bash
git status
```

Consultar cambios.

```bash
git add .
```

Preparar cambios.

```bash
git commit -m "Descripción del cambio"
```

Crear un commit.

```bash
git push
```

Enviar cambios al repositorio remoto.

---

# 16. GitHub Actions

GitHub Actions se utiliza para implementar el proceso de **Integración Continua (CI)**.

Cada vez que se realiza un cambio en el repositorio, el workflow puede ejecutar automáticamente diferentes validaciones.

El objetivo es detectar errores antes de integrar cambios al proyecto.

El pipeline puede seguir el siguiente proceso:

```text
       GitHub
          │
          ▼
   GitHub Actions
          │
          ▼
 Crear entorno Python
          │
          ▼
Instalar requirements.txt
          │
          ▼
      Ejecutar Flake8
          │
          ▼
   Levantar MySQL
          │
          ▼
      Ejecutar pytest
          │
          ▼
       Coverage
          │
          ▼
   Pipeline aprobado
```

---

# 17. Pipeline de CI

El pipeline tiene cuatro etapas principales.

## Etapa 1 — Preparación

Se configura Python y se crea el entorno necesario para ejecutar el proyecto.

```text
Python
  ↓
venv
  ↓
requirements.txt
```

---

## Etapa 2 — Calidad de código

Se ejecuta Flake8:

```bash
flake8 .
```

Si existen errores de estilo o problemas detectados por el linter, el pipeline puede detenerse.

---

## Etapa 3 — Pruebas automatizadas

Se levanta una instancia de MySQL para pruebas y posteriormente se ejecuta:

```bash
pytest
```

Si alguna prueba falla, el pipeline se marca como fallido.

---

## Etapa 4 — Cobertura

De manera opcional se ejecuta:

```bash
pytest --cov=.
```

El resultado permite conocer qué porcentaje del código está siendo probado.

---

# 18. Flujo de trabajo para nuevos integrantes

Cuando un nuevo integrante se incorpora al proyecto, debe seguir este procedimiento:

### Paso 1

Clonar el repositorio:

```bash
git clone URL_DEL_REPOSITORIO
```

### Paso 2

Entrar al proyecto:

```bash
cd NOMBRE_DEL_PROYECTO
```

### Paso 3

Crear el entorno virtual:

```bash
python -m venv venv
```

### Paso 4

Activar el entorno:

```bash
venv\Scripts\activate
```

### Paso 5

Instalar dependencias:

```bash
pip install -r requirements.txt
```

### Paso 6

Ejecutar las pruebas:

```bash
pytest
```

### Paso 7

Ejecutar el análisis de código:

```bash
flake8 .
```

### Paso 8

Ejecutar coverage, si está habilitado:

```bash
pytest --cov=.
```

### Paso 9

Comprobar el estado del repositorio:

```bash
git status
```

### Paso 10

Realizar los cambios correspondientes y crear un commit:

```bash
git add .
git commit -m "Descripción del cambio"
git push
```

---

# 19. Buenas prácticas del equipo

Para mantener un proyecto organizado se recomienda:

* No subir la carpeta `venv/` al repositorio.
* Mantener actualizado `requirements.txt`.
* Crear pruebas para las nuevas funcionalidades.
* Ejecutar `pytest` antes de realizar un push.
* Ejecutar `flake8` antes de crear un Pull Request.
* Utilizar mensajes de commit descriptivos.
* No almacenar contraseñas ni credenciales dentro del código.
* Utilizar variables de entorno para información sensible.
* Mantener actualizado el README.
* No modificar directamente código de otro integrante sin coordinación.
* Revisar que el pipeline de GitHub Actions haya finalizado correctamente.

---

# 20. Archivo .gitignore

La carpeta del entorno virtual no debe subirse a GitHub.

Se recomienda incluir:

```text
venv/
__pycache__/
*.pyc
.env
.pytest_cache/
.coverage
htmlcov/
```

Esto evita almacenar archivos temporales, credenciales o archivos generados automáticamente.

---

# 21. Checklist de onboarding

El nuevo integrante deberá comprobar:

* [ ] Tiene Python instalado.
* [ ] Tiene Git instalado.
* [ ] Tiene acceso al repositorio de GitHub.
* [ ] Clonó correctamente el proyecto.
* [ ] Creó el entorno virtual.
* [ ] Activó el entorno virtual.
* [ ] Instaló `requirements.txt`.
* [ ] Puede ejecutar `pytest`.
* [ ] Puede ejecutar `flake8`.
* [ ] Puede conectarse a la base de datos de desarrollo, si corresponde.
* [ ] Comprende la estructura básica del proyecto.
* [ ] Comprende el flujo Git → GitHub → GitHub Actions.
* [ ] Realizó correctamente un commit y push.
* [ ] El pipeline de CI termina correctamente.

---

# 22. Solución rápida de problemas

### Python no es reconocido

Comprobar la instalación:

```bash
python --version
```

Si no funciona, verificar que Python esté agregado al PATH.

### No se puede activar venv en Windows

Intentar desde CMD:

```bash
venv\Scripts\activate
```

Si se utiliza PowerShell y existen restricciones de ejecución, puede ser necesario ajustar la política de ejecución de PowerShell.

### pytest no se encuentra

Comprobar que el entorno virtual esté activo:

```bash
venv\Scripts\activate
```

Después:

```bash
pip install -r requirements.txt
```

### Flake8 muestra errores

Ejecutar:

```bash
flake8 .
```

Revisar los archivos y corregir los errores indicados antes de realizar el push.

### Las pruebas de MySQL fallan

Verificar:

* Que las credenciales utilizadas por las pruebas sean correctas.
* Que la configuración de conexión coincida con el entorno.
* Que la base de datos requerida exista.
* Que GitHub Actions haya levantado correctamente el servicio MySQL.

---

# 23. Objetivo DevOps del proyecto

El propósito de utilizar estas herramientas no es únicamente ejecutar el programa, sino establecer un proceso automatizado que permita comprobar continuamente la calidad del software.

El proyecto busca implementar el siguiente ciclo:

```text
DESARROLLO
    │
    ▼
   GIT
    │
    ▼
  GITHUB
    │
    ▼
GITHUB ACTIONS
    │
    ├──────────────┐
    ▼              ▼
  FLAKE8        PYTEST
                    │
                    ▼
                  MYSQL
                    │
                    ▼
                COVERAGE
                    │
                    ▼
             RESULTADO DEL CI
```

De esta manera, cada cambio realizado por el equipo puede ser validado automáticamente antes de incorporarse al proyecto.

---

# 24. Conclusión

El entorno del proyecto está diseñado para aplicar principios fundamentales de DevOps, principalmente **reproducibilidad, automatización, integración continua y control de calidad**.

Python proporciona el entorno de desarrollo, `venv` y `requirements.txt` permiten reproducir las dependencias, Flake8 automatiza el análisis de calidad, pytest ejecuta las pruebas, MySQL proporciona [...]

El objetivo final es que cualquier integrante autorizado pueda clonar el proyecto, configurar su entorno y comenzar a trabajar siguiendo un procedimiento estandarizado.

**Flujo principal:**

> **Código → Git → GitHub → GitHub Actions → Calidad → Pruebas → Base de datos → Coverage → Resultado del pipeline**
