# app/routes/estudiantes.py
from flask import Blueprint, jsonify, request
from app import db
from app.models.estudiante import Estudiante

estudiantes_bp = Blueprint('estudiantes', __name__, url_prefix='/api/estudiantes')

# ─────── CREATE: POST /api/estudiantes/ ────────────────────────────────
@estudiantes_bp.route("/", methods=["POST"])
def crear_estudiante():
    """
    Crea un nuevo estudiante
    ---
    tags:
      - Estudiantes
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            matricula: {type: string, example: "ITIC2024001"}
            nombre: {type: string, example: "Ana"}
            apellido: {type: string, example: "García López"}
            email: {type: string, example: "ana@universidad.edu.mx"}
            carrera: {type: string, example: "ITIC"}
            semestre: {type: integer, example: 5}
    responses:
      201:
        description: Estudiante creado exitosamente
      400:
        description: Datos inválidos o faltantes
      409:
        description: La matrícula ya existe
    """
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400

    campos_requeridos = ["matricula", "nombre", "apellido", "email", "carrera"]
    for campo in campos_requeridos:
        if campo not in datos:
            return jsonify({"error": f"El campo '{campo}' es requerido"}), 400

    if Estudiante.query.filter_by(matricula=datos["matricula"]).first():
        return jsonify({"error": "La matrícula ya está registrada"}), 409

    if Estudiante.query.filter_by(email=datos["email"]).first():
        return jsonify({"error": "El email ya está registrado"}), 409

    nuevo = Estudiante(
        matricula=datos["matricula"],
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        email=datos["email"],
        carrera=datos["carrera"],
        semestre=datos.get("semestre", 1)
    )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify({
        "mensaje": "Estudiante creado exitosamente",
        "estudiante": nuevo.to_dict()
    }), 201


# ─────── READ ALL: GET /api/estudiantes/ ──────────────────────────────
@estudiantes_bp.route("/", methods=["GET"])
def obtener_estudiantes():
    """
    Obtiene la lista de todos los estudiantes
    ---
    tags:
      - Estudiantes
    parameters:
      - name: carrera
        in: query
        type: string
        description: Filtrar por carrera
      - name: pagina
        in: query
        type: integer
        default: 1
      - name: por_pagina
        in: query
        type: integer
        default: 10
    responses:
      200:
        description: Lista de estudiantes
    """
    carrera = request.args.get("carrera")
    pagina = request.args.get("pagina", 1, type=int)
    por_pagina = request.args.get("por_pagina", 10, type=int)

    query = Estudiante.query.filter_by(activo=True)
    if carrera:
        query = query.filter_by(carrera=carrera)

    paginacion = query.paginate(page=pagina, per_page=por_pagina, error_out=False)

    return jsonify({
        "total": paginacion.total,
        "paginas": paginacion.pages,
        "pagina_actual": pagina,
        "por_pagina": por_pagina,
        "estudiantes": [e.to_dict() for e in paginacion.items]
    }), 200


# ─────── READ ONE: GET /api/estudiantes/<id> ──────────────────────────
@estudiantes_bp.route("/<int:id>", methods=["GET"])
def obtener_estudiante(id):
    """
    Obtiene un estudiante por ID
    ---
    tags:
      - Estudiantes
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID único del estudiante
    responses:
      200:
        description: Estudiante encontrado
      404:
        description: Estudiante no encontrado
    """
    estudiante = Estudiante.query.get_or_404(id, description="Estudiante no encontrado")
    return jsonify(estudiante.to_dict()), 200


# ─────── UPDATE: PUT /api/estudiantes/<id> ────────────────────────────
@estudiantes_bp.route("/<int:id>", methods=["PUT"])
def actualizar_estudiante(id):
    """
    Actualiza los datos de un estudiante
    ---
    tags:
      - Estudiantes
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          properties:
            nombre: {type: string}
            apellido: {type: string}
            email: {type: string}
            carrera: {type: string}
            semestre: {type: integer}
    responses:
      200:
        description: Estudiante actualizado
      404:
        description: Estudiante no encontrado
    """
    estudiante = Estudiante.query.get_or_404(id)
    datos = request.get_json()

    if "nombre" in datos:
        estudiante.nombre = datos["nombre"]
    if "apellido" in datos:
        estudiante.apellido = datos["apellido"]
    if "email" in datos:
        estudiante.email = datos["email"]
    if "carrera" in datos:
        estudiante.carrera = datos["carrera"]
    if "semestre" in datos:
        estudiante.semestre = datos["semestre"]

    db.session.commit()
    return jsonify({"mensaje": "Actualizado", "estudiante": estudiante.to_dict()}), 200


# ─────── DELETE: DELETE /api/estudiantes/<id> ─────────────────────────
@estudiantes_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_estudiante(id):
    """
    Elimina (desactiva) un estudiante - Borrado lógico
    ---
    tags:
      - Estudiantes
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Estudiante desactivado
      404:
        description: Estudiante no encontrado
    """
    estudiante = Estudiante.query.get_or_404(id)
    estudiante.activo = False  # Borrado lógico
    db.session.commit()
    return jsonify({"mensaje": f"Estudiante {estudiante.matricula} desactivado"}), 200
