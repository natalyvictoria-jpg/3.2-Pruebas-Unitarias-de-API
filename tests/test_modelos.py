# tests/test_modelos.py
import pytest
from app.models.estudiante import Estudiante
from app.models.usuario import Usuario
from app.models.materia import Materia

class TestModeloEstudiante:

    def test_crear_estudiante_con_datos_validos(self, db, app):
        with app.app_context():
            est = Estudiante(
                matricula="ITIC001", nombre="Maria",
                apellido="Gonzalez", email="maria@uni.edu.mx",
                carrera="ITIC", semestre=5
            )
            db.session.add(est)
            db.session.commit()
            assert est.id is not None
            assert est.nombre == "Maria"
            assert est.activo == True
            assert est.semestre == 5
            assert est.fecha_registro is not None
            db.session.delete(est)
            db.session.commit()

    def test_to_dict_contiene_campos_requeridos(self, db, app):
        with app.app_context():
            est = Estudiante(
                matricula="ITIC002", nombre="Pedro",
                apellido="Sosa", email="pedro@uni.edu.mx",
                carrera="ITIC", semestre=3
            )
            db.session.add(est)
            db.session.commit()
            resultado = est.to_dict()
            campos_esperados = ["id", "matricula", "nombre", "apellido",
                                "email", "carrera", "semestre", "activo",
                                "fecha_registro", "nombre_completo"]
            for campo in campos_esperados:
                assert campo in resultado, f"Falta el campo: {campo}"
            assert resultado["nombre_completo"] == "Pedro Sosa"
            assert resultado["activo"] == True
            db.session.delete(est)
            db.session.commit()

    def test_semestre_por_defecto_es_uno(self, db, app):
        with app.app_context():
            est = Estudiante(
                matricula="ITIC004", nombre="Ana",
                apellido="Cruz", email="ana@uni.edu.mx",
                carrera="ITIC"
            )
            db.session.add(est)
            db.session.commit()
            assert est.semestre == 1
            db.session.delete(est)
            db.session.commit()


class TestModeloUsuario:

    def test_password_se_hashea_al_guardar(self, db, app):
        with app.app_context():
            usuario = Usuario(username="profe01", email="profe@uni.mx")
            usuario.set_password("MiPassword123")
            assert usuario.password_hash != "MiPassword123"
            assert len(usuario.password_hash) > 50

    def test_check_password_valida_correctamente(self, db, app):
        with app.app_context():
            usuario = Usuario(username="profe02", email="profe2@uni.mx")
            usuario.set_password("Segura456!")
            assert usuario.check_password("Segura456!") == True
            assert usuario.check_password("incorrecta") == False
            assert usuario.check_password("") == False

    def test_rol_por_defecto_es_docente(self, db, app):
        with app.app_context():
            usuario = Usuario(username="nuevo_unico", email="nuevo_unico@uni.mx")
            usuario.set_password("pass")
            db.session.add(usuario)
            db.session.commit()
            assert usuario.rol == "docente"
            db.session.delete(usuario)
            db.session.commit()


class TestModeloMateria:

    def test_crear_materia_exitosamente(self, db, app):
        with app.app_context():
            materia = Materia(
                clave="PROG101", nombre="Programacion Web",
                creditos=5, docente="Dr. Hernandez"
            )
            db.session.add(materia)
            db.session.commit()
            assert materia.id is not None
            assert materia.clave == "PROG101"
            assert materia.creditos == 5
            db.session.delete(materia)
            db.session.commit()