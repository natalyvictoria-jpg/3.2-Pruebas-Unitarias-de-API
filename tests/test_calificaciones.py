# tests/test_calificaciones.py
import pytest

class TestRegistroCalificaciones:

    def setup_datos(self, client, sufijo="001"):
        """Crea un estudiante y una materia unicos por prueba."""
        est = client.post("/api/estudiantes/", json={
            "matricula": f"CAL{sufijo}",
            "nombre": "Pedro",
            "apellido": "Ruiz",
            "email": f"pedro{sufijo}@test.mx",
            "carrera": "ITIC",
            "semestre": 3
        })
        id_estudiante = est.get_json()["estudiante"]["id"]

        mat = client.post("/api/materias/", json={
            "clave": f"CALC{sufijo}",
            "nombre": "Calculo Diferencial",
            "creditos": 5,
            "docente": "Dr. Test"
        })
        id_materia = mat.get_json()["materia"]["id"]

        return id_estudiante, id_materia

    def test_registrar_calificacion_valida(self, client):
        id_est, id_mat = self.setup_datos(client, "A01")
        resp = client.post("/api/calificaciones/", json={
            "estudiante_id": id_est,
            "materia_id": id_mat,
            "calificacion": 87.5,
            "periodo": "2024-1"
        })
        assert resp.status_code == 201
        datos = resp.get_json()
        assert datos["calificacion"] == 87.5
        assert datos["aprobado"] == True

    def test_calificacion_reprobatoria(self, client):
        id_est, id_mat = self.setup_datos(client, "A02")
        resp = client.post("/api/calificaciones/", json={
            "estudiante_id": id_est,
            "materia_id": id_mat,
            "calificacion": 45.0
        })
        assert resp.status_code == 201
        assert resp.get_json()["aprobado"] == False

    def test_calificacion_exactamente_cero(self, client):
        id_est, id_mat = self.setup_datos(client, "A03")
        resp = client.post("/api/calificaciones/", json={
            "estudiante_id": id_est,
            "materia_id": id_mat,
            "calificacion": 0
        })
        assert resp.status_code == 201
        assert resp.get_json()["aprobado"] == False

    def test_calificacion_exactamente_cien(self, client):
        id_est, id_mat = self.setup_datos(client, "A04")
        resp = client.post("/api/calificaciones/", json={
            "estudiante_id": id_est,
            "materia_id": id_mat,
            "calificacion": 100
        })
        assert resp.status_code == 201
        assert resp.get_json()["aprobado"] == True

    @pytest.mark.parametrize("cal_invalida,sufijo", [
        (-1,  "B01"),
        (101, "B02"),
        (200, "B03"),
        (-50, "B04")
    ])
    def test_calificacion_fuera_de_rango(self, client, cal_invalida, sufijo):
        id_est, id_mat = self.setup_datos(client, sufijo)
        resp = client.post("/api/calificaciones/", json={
            "estudiante_id": id_est,
            "materia_id": id_mat,
            "calificacion": cal_invalida
        })
        assert resp.status_code == 400


class TestKardex:

    def test_kardex_calcula_promedio_correctamente(self, client):
        est = client.post("/api/estudiantes/", json={
            "matricula": "KAR001",
            "nombre": "Sofia",
            "apellido": "Vega",
            "email": "sofia.vega@test.mx",
            "carrera": "ITIC",
            "semestre": 5
        })
        id_est = est.get_json()["estudiante"]["id"]

        for clave, nombre, cal in [
            ("KAR101", "Matematicas", 80),
            ("KAR102", "Fisica",      90),
            ("KAR103", "Quimica",     70),
        ]:
            mat = client.post("/api/materias/", json={
                "clave": clave, "nombre": nombre, "creditos": 4
            }).get_json()["materia"]
            client.post("/api/calificaciones/", json={
                "estudiante_id": id_est,
                "materia_id": mat["id"],
                "calificacion": cal
            })

        resp = client.get(f"/api/estudiantes/{id_est}/kardex")
        assert resp.status_code == 200
        est = resp.get_json()["estadisticas"]
        assert est["promedio_general"] == 80.0
        assert est["total_materias"] == 3
        assert est["materias_aprobadas"] == 3
        assert est["materias_reprobadas"] == 0
        assert est["calificacion_maxima"] == 90
        assert est["calificacion_minima"] == 70

    def test_kardex_estatus_en_riesgo(self, client):
        est = client.post("/api/estudiantes/", json={
            "matricula": "KAR002",
            "nombre": "Luis",
            "apellido": "Paz",
            "email": "luis.paz@test.mx",
            "carrera": "ITIC",
            "semestre": 2
        })
        id_est = est.get_json()["estudiante"]["id"]

        mat = client.post("/api/materias/", json={
            "clave": "KAR201", "nombre": "Reprobada", "creditos": 3
        }).get_json()["materia"]

        client.post("/api/calificaciones/", json={
            "estudiante_id": id_est,
            "materia_id": mat["id"],
            "calificacion": 50
        })

        kardex = client.get(f"/api/estudiantes/{id_est}/kardex").get_json()
        assert kardex["estadisticas"]["estatus"] == "En riesgo"
        assert kardex["estadisticas"]["materias_reprobadas"] == 1

    def test_kardex_sin_calificaciones(self, client):
        est = client.post("/api/estudiantes/", json={
            "matricula": "KAR003",
            "nombre": "Ana",
            "apellido": "Mora",
            "email": "ana.mora@test.mx",
            "carrera": "ITIC",
            "semestre": 1
        })
        id_est = est.get_json()["estudiante"]["id"]
        resp = client.get(f"/api/estudiantes/{id_est}/kardex")
        assert resp.status_code == 200
        datos = resp.get_json()
        assert datos["calificaciones"] == []
        assert "mensaje" in datos