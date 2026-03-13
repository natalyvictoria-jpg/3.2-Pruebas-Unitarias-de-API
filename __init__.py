# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from .config import DevelopmentConfig

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    swagger_config = {
        "headers": [],
        "specs": [{"endpoint": "apispec", "route": "/apispec.json"}],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    swagger_template = {
        "info": {
            "title": "API Escolar + TechStore - ITIC",
            "version": "1.0.0",
            "description": "API REST completa con Flask y PostgreSQL"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Introduce: Bearer <tu_token>"
            }
        }
    }
    Swagger(app, config=swagger_config, template=swagger_template)

    # Registrar blueprints
    from .routes import main_bp
    from .routes.estudiantes import estudiantes_bp
    from .routes.auth import auth_bp
    from .routes.calificaciones import cal_bp
    from .routes.materias import materias_bp
    from .routes.tienda import tienda_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(estudiantes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cal_bp)
    app.register_blueprint(materias_bp)
    app.register_blueprint(tienda_bp)

    return app