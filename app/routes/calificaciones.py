# app/routes/calificaciones.py
from flask import Blueprint, jsonify, request
from app import db
from app.models.calificacion import Calificacion
from app.models.estudiante import Estudiante

cal_bp = Blueprint('calificaciones', __name__, url_prefix='/api')

@cal_bp.route("/estudiantes/<int:id>/kardex", methods=["GET"])
def obtener_kardex(id):
    """
    Obtiene el kardex completo de un estudiante con estadísticas
    ---
    tags:
      - Calificaciones
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID del estudiante
    responses:
      200:
        description: Kardex del estudiante con estadísticas
      404:
        description: Estudiante no encontrado
    """
    estudiante = Estudiante.query.get_or_404(id)
    calificaciones = Calificacion.query.filter_by(estudiante_id=id).all()

    if not calificaciones:
        return jsonify({
            "estudiante": estudiante.to_dict(),
            "mensaje": "Sin calificaciones registradas",
            "calificaciones": []
        }), 200

    valores = [float(c.calificacion) for c in calificaciones]
    promedio = sum(valores) / len(valores)
    materias_aprobadas = sum(1 for v in valores if v >= 60)

    return jsonify({
        "estudiante": estudiante.to_dict(),
        "estadisticas": {
            "promedio_general": round(promedio, 2),
            "total_materias": len(calificaciones),
            "materias_aprobadas": materias_aprobadas,
            "materias_reprobadas": len(calificaciones) - materias_aprobadas,
            "calificacion_maxima": max(valores),
            "calificacion_minima": min(valores),
            "estatus": "Regular" if promedio >= 70 else "En riesgo"
        },
        "calificaciones": [c.to_dict() for c in calificaciones]
    }), 200


@cal_bp.route("/calificaciones/", methods=["POST"])
def registrar_calificacion():
    """
    Registra una nueva calificación para un estudiante
    ---
    tags:
      - Calificaciones
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            estudiante_id: {type: integer, example: 1}
            materia_id: {type: integer, example: 1}
            calificacion: {type: number, example: 85.5}
            periodo: {type: string, example: "2024-1"}
    responses:
      201:
        description: Calificación registrada
      400:
        description: Calificación fuera de rango
    """
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400

    cal = datos.get("calificacion", 0)
    if not 0 <= float(cal) <= 100:
        return jsonify({"error": "La calificación debe estar entre 0 y 100"}), 400

    nueva = Calificacion(
        estudiante_id=datos["estudiante_id"],
        materia_id=datos["materia_id"],
        calificacion=cal,
        periodo=datos.get("periodo", "2024-1")
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify(nueva.to_dict()), 201


@cal_bp.route("/calificaciones/", methods=["GET"])
def obtener_calificaciones():
    """
    Obtiene todas las calificaciones
    ---
    tags:
      - Calificaciones
    responses:
      200:
        description: Lista de calificaciones
    """
    calificaciones = Calificacion.query.all()
    return jsonify({"calificaciones": [c.to_dict() for c in calificaciones]}), 200
