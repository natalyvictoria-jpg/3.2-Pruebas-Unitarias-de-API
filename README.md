# 3.2-Pruebas-Unitarias-de-API

<p align="center">
  <img width="100%" src="https://raw.githubusercontent.com/Platane/snk/output/github-contribution-grid-snake.svg" alt="" />
</p>

<h1 align="center">
  🌐💻 APLICACIONES WEB ORIENTADA A SERVICIOS
</h1>


## GTID153

📘 **Materia:** Aplicaciones Web Orientada a Servicios  
👩‍💻❤️ **Nombre:** Nataly Victoria Gonzalez Aviles  
🏫 **Proyecto o Actividad:** Pruebas Unitarias
📅 **Unidad:** 3  
⚙️ **Lenguaje:** Python  
🧠 **Propósito:** Desarrollar aplicaciones web utilizando APIs diferentes, aplicando los conocimientos adquiridos en la unidad 3 y comprendiendo su funcionamiento mediante su implementación en Python.  
👨‍🏫 **Docente:** Anastacio Rodriguez Garcia

 Implementé pruebas unitarias, de integración y End-to-End para una API REST con Flask y PostgreSQL usando pytest. El proyecto cuenta con 46 pruebas automatizadas con 86% de cobertura de código. Las pruebas usan SQLite en memoria para no afectar la base de datos real. Se probaron modelos, endpoints CRUD, autenticación JWT con control de roles, calificaciones con el kardex, y un flujo completo de compra E2E para la TechStore.

 ![pruebas](https://github.com/natalyvictoria-jpg/3.2-Pruebas-Unitarias-de-API/raw/main/uno.jpeg)

  ![pruebas](https://github.com/natalyvictoria-jpg/3.2-Pruebas-Unitarias-de-API/raw/main/dos.jpeg)

  ![pruebas](https://github.com/natalyvictoria-jpg/3.2-Pruebas-Unitarias-de-API/raw/main/tres.jpeg)


## 🎓 API Escolar + TechStore — Flask & PostgreSQL
API REST completa desarrollada en Python con Flask, PostgreSQL y SQLAlchemy como proyecto de la materia Aplicaciones Web Orientadas a Servicios (ITIC 2025-2026).


## 🚀 ¿Qué hace el proyecto?
El proyecto tiene dos módulos principales:
Módulo Escolar:

CRUD completo de estudiantes, materias y calificaciones
Kardex por estudiante con cálculo automático de promedio, materias aprobadas/reprobadas y estatus académico
Autenticación segura con JWT y control de acceso por roles (admin/docente)
Documentación interactiva con Swagger en /docs/

## Módulo TechStore:

Catálogo de productos con búsqueda, stock y categorías
Procesamiento de órdenes de compra con validación de stock en tiempo real
Gestión de clientes
Reporte de ventas exclusivo para administradores

## Archivos nuevos creados - Lo que se agrego al proyecto

| Archivo | Descripción |
|---|---|
| `tests/__init__.py` | Inicializador del paquete de pruebas |
| `tests/conftest.py` | Configuración y fixtures de pytest |
| `tests/test_modelos.py` | 7 pruebas unitarias de modelos |
| `tests/test_estudiantes.py` | 10 pruebas de integración CRUD |
| `tests/test_auth.py` | 13 pruebas de autenticación JWT |
| `tests/test_calificaciones.py` | 11 pruebas de calificaciones/kardex |
| `tests/test_tienda.py` | 5 pruebas E2E de la TechStore |
| `pytest.ini` | Configuración de pytest + cobertura |
| `app/models/tienda.py` | Modelos TechStore (nueva funcionalidad) |
| `app/routes/tienda.py` | Rutas TechStore (nueva funcionalidad) |


## 🧪 Pruebas Unitarias (Unidad 3)
Lo que diferencia este proyecto de una API básica es la suite completa de pruebas automatizadas implementada con pytest, pytest-flask y pytest-cov:
| Suite | Tipo | Pruebas |
|---|---|---|
| `test_modelos.py` | Unitarias | 7 |
| `test_estudiantes.py` | Integración | 10 |
| `test_auth.py` | Integración + Seguridad | 13 |
| `test_calificaciones.py` | Integración | 11 |
| `test_tienda.py` | End-to-End | 5 |
| **Total** | | **46 ✅** |


## 🛠 Tecnologías

Python 3.14 + Flask 3.x
PostgreSQL + SQLAlchemy + Flask-SQLAlchemy
Flask-JWT-Extended
Flasgger (Swagger UI)
pytest + pytest-flask + pytest-cov

## ▶️ Ejecutar pruebas

```bash 
# Todas las pruebas con cobertura
pytest

# Solo un módulo
pytest tests/test_modelos.py -v

# Pruebas que contengan una palabra clave
pytest -k "kardex" -v

# Ver las pruebas más lentas
pytest --durations=5
```

