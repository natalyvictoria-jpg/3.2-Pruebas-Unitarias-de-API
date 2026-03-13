# app/routes/auth.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.usuario import Usuario
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route("/registro", methods=["POST"])
def registro():
    """
    Registra un nuevo usuario en el sistema
    ---
    tags:
      - Autenticacion
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            username: {type: string, example: "docente1"}
            email: {type: string, example: "docente1@uni.edu.mx"}
            password: {type: string, example: "contrasena123"}
            rol: {type: string, example: "docente"}
    responses:
      201:
        description: Usuario creado exitosamente
      409:
        description: Username ya en uso
    """
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400

    for campo in ["username", "email", "password"]:
        if campo not in datos:
            return jsonify({"error": f"El campo '{campo}' es requerido"}), 400

    if Usuario.query.filter_by(username=datos["username"]).first():
        return jsonify({"error": "El username ya esta en uso"}), 409

    if Usuario.query.filter_by(email=datos["email"]).first():
        return jsonify({"error": "El email ya esta en uso"}), 409

    usuario = Usuario(
        username=datos["username"],
        email=datos["email"],
        rol=datos.get("rol", "docente")
    )
    usuario.set_password(datos["password"])

    db.session.add(usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario creado", "id": usuario.id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Autentica al usuario y devuelve un token JWT
    ---
    tags:
      - Autenticacion
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            username: {type: string, example: "docente1"}
            password: {type: string, example: "contrasena123"}
    responses:
      200:
        description: Login exitoso, retorna token JWT
      401:
        description: Credenciales invalidas
    """
    datos = request.get_json()
    usuario = Usuario.query.filter_by(username=datos["username"]).first()

    if not usuario or not usuario.check_password(datos["password"]):
        return jsonify({"error": "Credenciales invalidas"}), 401

    token = create_access_token(
        identity=str(usuario.id),
        expires_delta=timedelta(hours=24),
        additional_claims={"rol": usuario.rol}
    )

    return jsonify({
        "token": token,
        "tipo": "Bearer",
        "expira_en": "24 horas",
        "usuario": {
            "id": usuario.id,
            "username": usuario.username,
            "rol": usuario.rol
        }
    }), 200


@auth_bp.route("/perfil", methods=["GET"])
@jwt_required()
def perfil():
    """
    Obtiene el perfil del usuario autenticado
    ---
    tags:
      - Autenticacion
    security:
      - Bearer: []
    responses:
      200:
        description: Perfil del usuario
      401:
        description: Token invalido o no proporcionado
    """
    identidad = get_jwt_identity()
    claims = get_jwt()
    usuario = Usuario.query.get(int(identidad))
    return jsonify({"usuario": usuario.username, "rol": claims.get("rol")}), 200


@auth_bp.route("/admin/usuarios/<int:id>", methods=["DELETE"])
@jwt_required()
def eliminar_usuario(id):
    """
    Elimina un usuario - Solo accesible por admin
    ---
    tags:
      - Autenticacion
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Usuario desactivado
      403:
        description: Acceso denegado
      404:
        description: Usuario no encontrado
    """
    claims = get_jwt()
    if claims.get("rol") != "admin":
        return jsonify({"error": "Acceso denegado. Se requiere rol admin"}), 403
    usuario = Usuario.query.get_or_404(id)
    usuario.activo = False
    db.session.commit()
    return jsonify({"mensaje": f"Usuario {usuario.username} desactivado"}), 200