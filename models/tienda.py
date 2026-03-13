# app/models/tienda.py
from app import db
from datetime import datetime

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    productos   = db.relationship('Producto', back_populates='categoria')

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "descripcion": self.descripcion}

class Producto(db.Model):
    __tablename__ = 'productos'
    id             = db.Column(db.Integer, primary_key=True)
    sku            = db.Column(db.String(20), unique=True, nullable=False)
    nombre         = db.Column(db.String(200), nullable=False)
    descripcion    = db.Column(db.Text)
    precio         = db.Column(db.Numeric(10, 2), nullable=False)
    stock          = db.Column(db.Integer, default=0)
    categoria_id   = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    activo         = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    categoria      = db.relationship('Categoria', back_populates='productos')
    detalles       = db.relationship('DetalleOrden', back_populates='producto')

    def to_dict(self):
        return {
            "id": self.id, "sku": self.sku, "nombre": self.nombre,
            "descripcion": self.descripcion, "precio": float(self.precio),
            "stock": self.stock, "activo": self.activo,
            "categoria_id": self.categoria_id
        }

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id        = db.Column(db.Integer, primary_key=True)
    nombre    = db.Column(db.String(100), nullable=False)
    email     = db.Column(db.String(120), unique=True, nullable=False)
    telefono  = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    ordenes   = db.relationship('Orden', back_populates='cliente')

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre,
                "email": self.email, "telefono": self.telefono}

class Orden(db.Model):
    __tablename__ = 'ordenes'
    id         = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    total      = db.Column(db.Numeric(10, 2), nullable=False)
    estado     = db.Column(db.String(20), default='pendiente')
    fecha      = db.Column(db.DateTime, default=datetime.utcnow)
    cliente    = db.relationship('Cliente', back_populates='ordenes')
    detalles   = db.relationship('DetalleOrden', back_populates='orden')

    def to_dict(self):
        return {
            "id": self.id, "cliente_id": self.cliente_id,
            "total": float(self.total), "estado": self.estado,
            "fecha": self.fecha.isoformat()
        }

class DetalleOrden(db.Model):
    __tablename__ = 'detalle_ordenes'
    id              = db.Column(db.Integer, primary_key=True)
    orden_id        = db.Column(db.Integer, db.ForeignKey('ordenes.id'))
    producto_id     = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad        = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    orden           = db.relationship('Orden', back_populates='detalles')
    producto        = db.relationship('Producto', back_populates='detalles')

    def to_dict(self):
        return {
            "id": self.id, "orden_id": self.orden_id,
            "producto_id": self.producto_id, "cantidad": self.cantidad,
            "precio_unitario": float(self.precio_unitario)
        }