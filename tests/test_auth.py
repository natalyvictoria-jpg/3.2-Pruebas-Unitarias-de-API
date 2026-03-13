# tests/test_auth.py

import pytest
from app.models.usuario import Usuario

class TestRegistro:

    def test_registro_exitoso(self, client):
        resp = client.post("/api/auth/registro", json={
            "username": "nuevo_docente",
            "email": "nuevo@uni.mx",
            "password": "Segura123!",
            "rol": "docente"
        })
        assert resp.status_code == 201
        datos = resp.get_json()
        assert "id" in datos
        assert "mensaje" in datos

    def test_username_duplicado_retorna_409(self, client):
        payload = {
            "username": "duplicado",
            "email": "a@test.mx",
            "password": "Pass1234!",
            "rol": "docente"
        }
        client.post("/api/auth/registro", json=payload)
        payload["email"] = "b@test.mx"
        resp = client.post("/api/auth/registro", json=payload)
        assert resp.status_code == 409

    def test_campos_requeridos_faltantes(self, client):
        resp = client.post("/api/auth/registro", json={
            "username": "sinpassword"
        })
        assert resp.status_code == 400


class TestLogin:

    def test_login_exitoso_retorna_token(self, client):
        client.post("/api/auth/registro", json={
            "username": "user_login",
            "email": "ul@test.mx",
            "password": "LoginPass1!"
        })
        resp = client.post("/api/auth/login", json={
            "username": "user_login",
            "password": "LoginPass1!"
        })
        assert resp.status_code == 200
        datos = resp.get_json()
        assert "token" in datos
        assert len(datos["token"]) > 50
        assert datos["tipo"] == "Bearer"
        assert datos["usuario"]["username"] == "user_login"

    def test_password_incorrecta_retorna_401(self, client):
        client.post("/api/auth/registro", json={
            "username": "user_401",
            "email": "u401@test.mx",
            "password": "CorrectPass1!"
        })
        resp = client.post("/api/auth/login", json={
            "username": "user_401",
            "password": "PasswordIncorrecta!"
        })
        assert resp.status_code == 401
        assert "error" in resp.get_json()

    def test_usuario_inexistente_retorna_401(self, client):
        resp = client.post("/api/auth/login", json={
            "username": "noexisto",
            "password": "cualquiera"
        })
        assert resp.status_code == 401


class TestRutasProtegidas:

    def test_ruta_protegida_sin_token_retorna_401(self, client):
        resp = client.get("/api/auth/perfil")
        assert resp.status_code == 401

    def test_ruta_protegida_con_token_valido(self, client):
        # Registrar y hacer login en el mismo client
        client.post("/api/auth/registro", json={
            "username": "user_perfil",
            "email": "perfil@test.mx",
            "password": "Perfil123!"
        })
        resp_login = client.post("/api/auth/login", json={
            "username": "user_perfil",
            "password": "Perfil123!"
        })
        token = resp_login.get_json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/api/auth/perfil", headers=headers)
        assert resp.status_code == 200
        assert "usuario" in resp.get_json()
        
    def test_token_manipulado_retorna_error(self, client):
        token_falso = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJoYWNrZXIifQ.firma_falsa"
        headers = {"Authorization": f"Bearer {token_falso}"}
        resp = client.get("/api/auth/perfil", headers=headers)
        assert resp.status_code in [401, 422]

    def test_header_sin_bearer_retorna_error(self, client):
        headers = {"Authorization": "token_directo_sin_bearer"}
        resp = client.get("/api/auth/perfil", headers=headers)
        assert resp.status_code in [401, 422]

class TestControlDeRoles:
    """
    Prueba que solo los usuarios con el rol correcto
    pueden acceder a ciertas rutas.
    """

    def test_docente_no_puede_eliminar_usuarios(self, client):
        """
        Un usuario con rol 'docente' NO debe poder acceder
        a rutas exclusivas de 'admin'. Debe retornar 403 Forbidden.
        """
        # Registrar y loguear como docente
        client.post("/api/auth/registro", json={
            "username": "docente_roles",
            "email": "docente_roles@uni.mx",
            "password": "Docente123!",
            "rol": "docente"
        })
        resp_login = client.post("/api/auth/login", json={
            "username": "docente_roles",
            "password": "Docente123!"
        })
        token = resp_login.get_json()["token"]
        headers_docente = {"Authorization": f"Bearer {token}"}

        # Intentar eliminar usuario con rol docente
        resp = client.delete("/api/auth/admin/usuarios/1", headers=headers_docente)
        assert resp.status_code == 403
        assert "error" in resp.get_json()

    def test_admin_puede_eliminar_usuarios(self, client):
        """
        Un usuario con rol 'admin' SÍ puede acceder
        a rutas exclusivas de admin. Debe retornar 200.
        """
        # Crear usuario a eliminar
        client.post("/api/auth/registro", json={
            "username": "usuario_a_eliminar",
            "email": "eliminar@uni.mx",
            "password": "Eliminar123!",
            "rol": "docente"
        })
        id_usuario = Usuario.query.filter_by(
            username="usuario_a_eliminar"
        ).first()

        # Registrar y loguear como admin
        client.post("/api/auth/registro", json={
            "username": "admin_roles",
            "email": "admin_roles@uni.mx",
            "password": "Admin123!",
            "rol": "admin"
        })
        resp_login = client.post("/api/auth/login", json={
            "username": "admin_roles",
            "password": "Admin123!"
        })
        token = resp_login.get_json()["token"]
        headers_admin = {"Authorization": f"Bearer {token}"}

        # Admin elimina usuario
        resp = client.delete(
            f"/api/auth/admin/usuarios/{id_usuario.id}",
            headers=headers_admin
        )
        assert resp.status_code == 200
        assert "mensaje" in resp.get_json()

    def test_sin_token_no_puede_eliminar(self, client):
        """Sin token no se puede acceder a rutas de admin."""
        resp = client.delete("/api/auth/admin/usuarios/1")
        assert resp.status_code == 401