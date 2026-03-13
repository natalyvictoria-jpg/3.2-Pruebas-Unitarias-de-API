# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-por-defecto-insegura")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-clave-insegura")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Configuracion exclusiva para pruebas. Usa SQLite en memoria."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = False
    SQLALCHEMY_ECHO = False
    JWT_SECRET_KEY = "clave-secreta-para-pruebas-unitarias-flask-2024"
    SECRET_KEY = "clave-secreta-para-pruebas-unitarias-flask-2024"
    