# run.py - Ejecutar con: python run.py
from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Tablas creadas correctamente")

    print("🚀 Servidor iniciado en http://localhost:5000")
    print("📄 Documentación Swagger: http://localhost:5000/docs/")
    app.run(host='0.0.0.0', port=5000, debug=True)
