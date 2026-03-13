# app/routes/tienda.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models.tienda import Categoria, Producto, Cliente, Orden, DetalleOrden

tienda_bp = Blueprint('tienda', __name__)

# ─── CATEGORIAS ───────────────────────────────────────────────────────

@tienda_bp.route("/api/categorias/", methods=["GET"])
def obtener_categorias():
    categorias = Categoria.query.all()
    return jsonify({"categorias": [c.to_dict() for c in categorias]}), 200

@tienda_bp.route("/api/categorias/", methods=["POST"])
@jwt_required()
def crear_categoria():
    datos = request.get_json()
    if not datos or "nombre" not in datos:
        return jsonify({"error": "El campo nombre es requerido"}), 400
    if Categoria.query.filter_by(nombre=datos["nombre"]).first():
        return jsonify({"error": "La categoria ya existe"}), 409
    nueva = Categoria(nombre=datos["nombre"], descripcion=datos.get("descripcion"))
    db.session.add(nueva)
    db.session.commit()
    return jsonify({"categoria": nueva.to_dict()}), 201

# ─── PRODUCTOS ────────────────────────────────────────────────────────

@tienda_bp.route("/api/productos/", methods=["GET"])
def obtener_productos():
    buscar = request.args.get("buscar")
    query = Producto.query.filter_by(activo=True)
    if buscar:
        query = query.filter(Producto.nombre.ilike(f"%{buscar}%"))
    productos = query.all()
    return jsonify({"productos": [p.to_dict() for p in productos]}), 200

@tienda_bp.route("/api/productos/", methods=["POST"])
@jwt_required()
def crear_producto():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400
    for campo in ["sku", "nombre", "precio"]:
        if campo not in datos:
            return jsonify({"error": f"El campo {campo} es requerido"}), 400
    if Producto.query.filter_by(sku=datos["sku"]).first():
        return jsonify({"error": "El SKU ya existe"}), 409
    nuevo = Producto(
        sku=datos["sku"],
        nombre=datos["nombre"],
        descripcion=datos.get("descripcion"),
        precio=datos["precio"],
        stock=datos.get("stock", 0),
        categoria_id=datos.get("categoria_id")
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"producto": nuevo.to_dict()}), 201

@tienda_bp.route("/api/productos/<int:id>", methods=["GET"])
def obtener_producto(id):
    producto = Producto.query.get_or_404(id)
    return jsonify(producto.to_dict()), 200

@tienda_bp.route("/api/productos/<int:id>", methods=["PUT"])
@jwt_required()
def actualizar_producto(id):
    producto = Producto.query.get_or_404(id)
    datos = request.get_json()
    if "nombre" in datos:
        producto.nombre = datos["nombre"]
    if "precio" in datos:
        producto.precio = datos["precio"]
    if "stock" in datos:
        producto.stock = datos["stock"]
    if "descripcion" in datos:
        producto.descripcion = datos["descripcion"]
    db.session.commit()
    return jsonify({"producto": producto.to_dict()}), 200

@tienda_bp.route("/api/productos/<int:id>", methods=["DELETE"])
@jwt_required()
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    producto.activo = False
    db.session.commit()
    return jsonify({"mensaje": f"Producto {producto.sku} desactivado"}), 200

# ─── CLIENTES ─────────────────────────────────────────────────────────

@tienda_bp.route("/api/clientes/", methods=["GET"])
@jwt_required()
def obtener_clientes():
    clientes = Cliente.query.all()
    return jsonify({"clientes": [c.to_dict() for c in clientes]}), 200

@tienda_bp.route("/api/clientes/", methods=["POST"])
def crear_cliente():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400
    for campo in ["nombre", "email"]:
        if campo not in datos:
            return jsonify({"error": f"El campo {campo} es requerido"}), 400
    if Cliente.query.filter_by(email=datos["email"]).first():
        return jsonify({"error": "El email ya existe"}), 409
    nuevo = Cliente(
        nombre=datos["nombre"],
        email=datos["email"],
        telefono=datos.get("telefono"),
        direccion=datos.get("direccion")
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"cliente": nuevo.to_dict()}), 201

# ─── ORDENES ──────────────────────────────────────────────────────────

@tienda_bp.route("/api/ordenes/", methods=["POST"])
@jwt_required()
def procesar_orden():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400

    total = 0
    detalles = []
    errores = []

    for item in datos.get("productos", []):
        producto = Producto.query.get(item["producto_id"])
        if not producto:
            errores.append(f"Producto ID {item['producto_id']} no existe")
            continue
        if producto.stock < item["cantidad"]:
            errores.append(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}")
            continue
        subtotal = float(producto.precio) * item["cantidad"]
        total += subtotal
        detalles.append({
            "producto": producto,
            "cantidad": item["cantidad"],
            "precio_unitario": float(producto.precio)
        })

    if errores:
        return jsonify({"error": "No se pudo procesar", "detalles": errores}), 400

    try:
        orden = Orden(cliente_id=datos["cliente_id"], total=total)
        db.session.add(orden)
        db.session.flush()

        for d in detalles:
            detalle = DetalleOrden(
                orden_id=orden.id,
                producto_id=d["producto"].id,
                cantidad=d["cantidad"],
                precio_unitario=d["precio_unitario"]
            )
            db.session.add(detalle)
            d["producto"].stock -= d["cantidad"]

        db.session.commit()
        return jsonify({
            "mensaje": "Orden procesada exitosamente",
            "orden_id": orden.id,
            "total": total,
            "productos_comprados": len(detalles)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error interno", "detalle": str(e)}), 500

# ─── REPORTES ─────────────────────────────────────────────────────────

@tienda_bp.route("/api/reportes/ventas", methods=["GET"])
@jwt_required()
def reporte_ventas():
    claims = get_jwt()
    if claims.get("rol") != "admin":
        return jsonify({"error": "Acceso denegado. Se requiere rol admin"}), 403

    from sqlalchemy import func, extract
    from datetime import datetime as dt

    mes  = request.args.get("mes",  dt.now().month, type=int)
    anio = request.args.get("anio", dt.now().year,  type=int)

    resultado = db.session.query(
        func.count(Orden.id).label("total_ordenes"),
        func.sum(Orden.total).label("ingresos_totales"),
        func.avg(Orden.total).label("ticket_promedio")
    ).filter(
        extract("month", Orden.fecha) == mes,
        extract("year",  Orden.fecha) == anio
    ).first()

    top_productos = db.session.query(
        Producto.nombre,
        func.sum(DetalleOrden.cantidad).label("unidades"),
        func.sum(DetalleOrden.cantidad * DetalleOrden.precio_unitario).label("revenue")
    ).join(DetalleOrden).group_by(Producto.nombre
    ).order_by(func.sum(DetalleOrden.cantidad).desc()).limit(5).all()

    return jsonify({
        "periodo": f"{mes}/{anio}",
        "resumen": {
            "total_ordenes": resultado.total_ordenes or 0,
            "ingresos": float(resultado.ingresos_totales or 0),
            "ticket_promedio": float(resultado.ticket_promedio or 0)
        },
        "top_productos": [
            {"producto": p.nombre, "unidades": p.unidades, "revenue": float(p.revenue)}
            for p in top_productos
        ]
    }), 200