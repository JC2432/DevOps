# Herramientas DevOps — Proyecto | Habilidades DevOps

**Materia:** Habilidades DevOps
**Stack del sistema:** Python (frontend y backend) + MySQL
**Contexto:** Proyecto

---

## 1. Python

**Versión recomendada:** Python 3.14.0 (estable y con amplio soporte de librerías) —  tiene mayor compatibilidad probada con paquetes de terceros.

**Función:** Lenguaje del backend y frontend del sistema.

**Por qué la usamos:** Es el stack ya definido para el proyecto; fijar una versión concreta es lo que hace reproducible el entorno de CI.

## 2. pytest

**Versión recomendada:** 9.1.1

**Función:** Framework de pruebas automatizadas para Python.

**Por qué la usamos:** Valida que las funciones del backend sigan funcionando conforme el equipo agrega o modifica código. Sin pruebas automáticas, el pipeline de CI solo estaría "ejecutando código" sin comprobar nada real.

## 3. flake8

**Versión recomendada:** 7.3.0

**Función:** Linter de estilo de código para Python (basado en PEP8).

**Por qué la usamos:** Mantiene consistencia de estilo entre los distintos miembros del equipo que trabajan en el mismo backend. Se integra como un paso más del pipeline de CI, mostrando control de calidad de código automatizado.

## 4. venv + requirements.txt

**Versión recomendada:** `venv` viene incluido con Python 3.13, no requiere versión aparte. `pip` ≥ 24.x (se actualiza junto con Python).

**Función:** Entorno virtual de Python y archivo de dependencias fijas.

**Por qué la usamos:** Garantiza que el proyecto sea reproducible — cualquier miembro del equipo (o quien lo evalúe) puede levantar exactamente el mismo entorno con `pip install -r requirements.txt`, sin conflictos de versiones entre máquinas.

## 5. MySQL 

**Versión recomendada:** MySQL 8.0.46 LTS 

**Función:** Sistema de gestión de base de datos relacional.

**Por qué la usamos:** Es la base de datos ya definida para el sistema. Para las pruebas automáticas, GitHub Actions puede levantar una instancia de MySQL como *service container* dentro del propio workflow (imagen `mysql:8.4`), sin necesidad de un servidor externo ni de Docker por parte del equipo.

## 6. Coverage (`pytest-cov`) — *opcional*

**Versión recomendada:** la más reciente publicada en marzo de 2026 (verificar `pip index versions pytest-cov` al momento de instalar, ya que se actualiza con frecuencia)

**Función:** Mide el porcentaje de código cubierto por las pruebas automáticas.

**Por qué la usamos:** Es un complemento sencillo que agrega valor al pipeline de CI, mostrando qué tan probado está el sistema — una métrica que suele valorarse en proyectos académicos de ingeniería de software.

---

## Flujo general

```
Git / GitHub  (código y documentación del proyecto)
      │
      ▼
GitHub Actions (CI)
      ├─ venv + requirements.txt   → entorno reproducible
      ├─ flake8                    → calidad de código
      ├─ pytest + MySQL de prueba  → pruebas automáticas
      └─ coverage (opcional)       → métricas de cobertura
```

