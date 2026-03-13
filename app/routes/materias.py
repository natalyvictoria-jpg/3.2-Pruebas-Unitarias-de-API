# app/routes/materias.py
from flask import Blueprint, jsonify, request
from app import db
from app.models.materia import Materia

materias_bp = Blueprint('materias', __name__, url_prefix='/api/materias')

@materias_bp.route("/", methods=["GET"])
def obtener_materias():
    """
    Obtiene todas las materias
    ---
    tags:
      - Materias
    responses:
      200:
        description: Lista de materias
    """
    materias = Materia.query.all()
    return jsonify({"materias": [m.to_dict() for m in materias]}), 200

@materias_bp.route("/", methods=["POST"])
def crear_materia():
    """
    Crea una nueva materia
    ---
    tags:
      - Materias
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            clave: {type: string, example: "MAT101"}
            nombre: {type: string, example: "Matemáticas I"}
            creditos: {type: integer, example: 5}
            docente: {type: string, example: "Dr. Pérez"}
    responses:
      201:
        description: Materia creada
      409:
        description: Clave duplicada
    """
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400

    for campo in ["clave", "nombre", "creditos"]:
        if campo not in datos:
            return jsonify({"error": f"El campo '{campo}' es requerido"}), 400

    if Materia.query.filter_by(clave=datos["clave"]).first():
        return jsonify({"error": "La clave ya existe"}), 409

    nueva = Materia(
        clave=datos["clave"],
        nombre=datos["nombre"],
        creditos=datos["creditos"],
        docente=datos.get("docente")
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify({"mensaje": "Materia creada", "materia": nueva.to_dict()}), 201

@materias_bp.route("/<int:id>", methods=["GET"])
def obtener_materia(id):
    """
    Obtiene una materia por ID
    ---
    tags:
      - Materias
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Materia encontrada
      404:
        description: Materia no encontrada
    """
    materia = Materia.query.get_or_404(id, description="Materia no encontrada")
    return jsonify(materia.to_dict()), 200

@materias_bp.route("/<int:id>", methods=["PUT"])
def actualizar_materia(id):
    """
    Actualiza una materia
    ---
    tags:
      - Materias
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Materia actualizada
    """
    materia = Materia.query.get_or_404(id)
    datos = request.get_json()
    if "nombre" in datos:
        materia.nombre = datos["nombre"]
    if "creditos" in datos:
        materia.creditos = datos["creditos"]
    if "docente" in datos:
        materia.docente = datos["docente"]
    db.session.commit()
    return jsonify({"mensaje": "Actualizado", "materia": materia.to_dict()}), 200

@materias_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_materia(id):
    """
    Elimina una materia
    ---
    tags:
      - Materias
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Materia eliminada
    """
    materia = Materia.query.get_or_404(id)
    db.session.delete(materia)
    db.session.commit()
    return jsonify({"mensaje": f"Materia '{materia.nombre}' eliminada"}), 200
