# tests/test_estudiantes.py
import pytest

class TestCrearEstudiante:

    def test_crear_estudiante_exitoso(self, client, estudiante_data):
        respuesta = client.post("/api/estudiantes/", json=estudiante_data)
        datos = respuesta.get_json()
        assert respuesta.status_code == 201
        assert "estudiante" in datos
        assert datos["estudiante"]["matricula"] == "TEST001"
        assert datos["estudiante"]["nombre"] == "Carlos"
        assert "id" in datos["estudiante"]

    def test_matricula_duplicada_retorna_409(self, client, estudiante_data):
        client.post("/api/estudiantes/", json=estudiante_data)
        respuesta = client.post("/api/estudiantes/", json=estudiante_data)
        assert respuesta.status_code == 409
        assert "error" in respuesta.get_json()

    def test_campo_email_requerido(self, client):
        datos_incompletos = {
            "matricula": "INC001",
            "nombre": "Sin Email",
            "apellido": "Test",
            "carrera": "ITIC"
        }
        respuesta = client.post("/api/estudiantes/", json=datos_incompletos)
        assert respuesta.status_code == 400
        assert "error" in respuesta.get_json()

    def test_body_vacio_retorna_400(self, client):
        respuesta = client.post("/api/estudiantes/", data="")
        assert respuesta.status_code in [400, 415]


class TestObtenerEstudiante:

    def test_lista_devuelve_200(self, client):
        respuesta = client.get("/api/estudiantes/")
        assert respuesta.status_code == 200
        datos = respuesta.get_json()
        assert "estudiantes" in datos
        assert "total" in datos
        assert "paginas" in datos

    def test_lista_vacia_retorna_lista(self, client):
        respuesta = client.get("/api/estudiantes/")
        datos = respuesta.get_json()
        assert respuesta.status_code == 200
        assert isinstance(datos["estudiantes"], list)

    def test_obtener_por_id_existente(self, client):
        datos = {
            "matricula": "GET001",
            "nombre": "Laura",
            "apellido": "Torres",
            "email": "laura@test.edu.mx",
            "carrera": "ITIC",
            "semestre": 3
        }
        post_resp = client.post("/api/estudiantes/", json=datos)
        assert post_resp.status_code == 201
        id_creado = post_resp.get_json()["estudiante"]["id"]
        respuesta = client.get(f"/api/estudiantes/{id_creado}")
        assert respuesta.status_code == 200
        assert respuesta.get_json()["id"] == id_creado

    def test_id_inexistente_retorna_404(self, client):
        respuesta = client.get("/api/estudiantes/99999")
        assert respuesta.status_code == 404


class TestActualizarEstudiante:

    def test_actualizar_semestre(self, client):
        datos = {
            "matricula": "UPD001",
            "nombre": "Mario",
            "apellido": "Lopez",
            "email": "mario@test.edu.mx",
            "carrera": "ITIC",
            "semestre": 2
        }
        post_resp = client.post("/api/estudiantes/", json=datos)
        assert post_resp.status_code == 201
        id_est = post_resp.get_json()["estudiante"]["id"]
        resp = client.put(f"/api/estudiantes/{id_est}", json={"semestre": 8})
        assert resp.status_code == 200
        assert resp.get_json()["estudiante"]["semestre"] == 8


class TestEliminarEstudiante:

    def test_borrado_logico(self, client):
        datos = {
            "matricula": "DEL001",
            "nombre": "Rosa",
            "apellido": "Medina",
            "email": "rosa@test.edu.mx",
            "carrera": "ITIC",
            "semestre": 4
        }
        post_resp = client.post("/api/estudiantes/", json=datos)
        assert post_resp.status_code == 201
        id_est = post_resp.get_json()["estudiante"]["id"]
        resp_del = client.delete(f"/api/estudiantes/{id_est}")
        assert resp_del.status_code == 200
        lista = client.get("/api/estudiantes/").get_json()["estudiantes"]
        ids_activos = [e["id"] for e in lista]
        assert id_est not in ids_activos