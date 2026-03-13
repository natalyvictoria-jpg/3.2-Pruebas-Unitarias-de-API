# tests/test_tienda.py
import pytest

class TestFlujoCompleto:

    def _crear_admin(self, client):
        """Helper: registra admin y retorna su token."""
        client.post("/api/auth/registro", json={
            "username": "admin_tienda",
            "email": "admin@techstore.mx",
            "password": "Admin123!",
            "rol": "admin"
        })
        resp = client.post("/api/auth/login", json={
            "username": "admin_tienda",
            "password": "Admin123!"
        })
        return resp.get_json()["token"]

    def _crear_cliente(self, client):
        """Helper: registra cliente y retorna su token."""
        client.post("/api/auth/registro", json={
            "username": "cliente01",
            "email": "cliente@gmail.com",
            "password": "Cliente123!",
            "rol": "cliente"
        })
        resp = client.post("/api/auth/login", json={
            "username": "cliente01",
            "password": "Cliente123!"
        })
        return resp.get_json()["token"]
    
    def _crear_productos(self, client, headers_admin, sufijo=""):
        """Helper: crea categoria y productos, retorna sus IDs."""
        client.post("/api/categorias/", json={
            "nombre": f"Laptops{sufijo}",
            "descripcion": "Computadoras portatiles"
        }, headers=headers_admin)

        client.post("/api/categorias/", json={
            "nombre": f"Accesorios{sufijo}",
            "descripcion": "Perifericos"
        }, headers=headers_admin)

        cat1 = client.get("/api/categorias/").get_json()["categorias"]
        id_cat1 = cat1[0]["id"]
        id_cat2 = cat1[1]["id"] if len(cat1) > 1 else cat1[0]["id"]

        laptop = client.post("/api/productos/", json={
            "sku": f"LAP{sufijo}001",
            "nombre": "Laptop Gamer 15",
            "precio": 18999.00,
            "stock": 10,
            "categoria_id": id_cat1
        }, headers=headers_admin)

        mouse = client.post("/api/productos/", json={
            "sku": f"MOU{sufijo}001",
            "nombre": "Mouse Inalambrico",
            "precio": 349.00,
            "stock": 50,
            "categoria_id": id_cat2
        }, headers=headers_admin)

        usb = client.post("/api/productos/", json={
            "sku": f"USB{sufijo}001",
            "nombre": "USB Hub 7 puertos",
            "precio": 199.00,
            "stock": 30,
            "categoria_id": id_cat2
        }, headers=headers_admin)

        return {
            "laptop": laptop.get_json()["producto"],
            "mouse":  mouse.get_json()["producto"],
            "usb":    usb.get_json()["producto"]
        }
  

    def test_flujo_completo_compra(self, client):
        """
        PRUEBA MAESTRA: flujo completo de principio a fin.
        1. Admin crea productos
        2. Cliente se registra
        3. Cliente busca productos
        4. Cliente procesa una orden
        5. Verificar que el stock se redujo
        6. Admin consulta reporte de ventas
        """
        # PASO 1: Admin crea productos
        token_admin = self._crear_admin(client)
        headers_admin = {"Authorization": f"Bearer {token_admin}"}
        productos = self._crear_productos(client, headers_admin)
        assert len(productos) == 3

        # PASO 2: Cliente registrado
        token_cliente = self._crear_cliente(client)
        assert token_cliente is not None
        headers_cliente = {"Authorization": f"Bearer {token_cliente}"}

        # PASO 3: Cliente busca laptops
        resp_busqueda = client.get("/api/productos/?buscar=laptop")
        assert resp_busqueda.status_code == 200
        resultados = resp_busqueda.get_json()["productos"]
        assert any("Laptop" in p["nombre"] for p in resultados)

        # PASO 4: Crear cliente y procesar orden
        cliente_resp = client.post("/api/clientes/", json={
            "nombre": "Juan Perez",
            "email": "juan@gmail.com"
        })
        assert cliente_resp.status_code == 201
        id_cliente = cliente_resp.get_json()["cliente"]["id"]

        id_laptop = productos["laptop"]["id"]
        id_mouse  = productos["mouse"]["id"]
        stock_inicial_laptop = productos["laptop"]["stock"]

        resp_orden = client.post("/api/ordenes/", json={
            "cliente_id": id_cliente,
            "productos": [
                {"producto_id": id_laptop, "cantidad": 2},
                {"producto_id": id_mouse,  "cantidad": 5}
            ]
        }, headers=headers_cliente)

        assert resp_orden.status_code == 201
        orden = resp_orden.get_json()
        assert orden["productos_comprados"] == 2
        assert orden["total"] > 0
        assert "orden_id" in orden

        # PASO 5: Verificar que el stock se redujo
        resp_prod = client.get(f"/api/productos/{id_laptop}")
        stock_actual = resp_prod.get_json()["stock"]
        assert stock_actual == stock_inicial_laptop - 2

        # PASO 6: Admin consulta reporte
        resp_reporte = client.get("/api/reportes/ventas", headers=headers_admin)
        assert resp_reporte.status_code == 200
        reporte = resp_reporte.get_json()
        assert reporte["resumen"]["total_ordenes"] >= 1
        assert reporte["resumen"]["ingresos"] > 0
        assert len(reporte["top_productos"]) >= 1

    def test_orden_stock_insuficiente(self, client):
        """
        CASO NEGATIVO: intentar comprar mas unidades de las disponibles.
        La orden completa debe ser rechazada.
        """
        token_admin = self._crear_admin(client)
        headers_admin = {"Authorization": f"Bearer {token_admin}"}
        productos = self._crear_productos(client, headers_admin, sufijo="B")

        token_cliente = self._crear_cliente(client)
        headers_cliente = {"Authorization": f"Bearer {token_cliente}"}

        cliente_resp = client.post("/api/clientes/", json={
            "nombre": "Maria Lopez",
            "email": "maria@gmail.com"
        })
        id_cliente = cliente_resp.get_json()["cliente"]["id"]

        id_usb = productos["usb"]["id"]

        # Intentar comprar 999 unidades (hay solo 30)
        resp = client.post("/api/ordenes/", json={
            "cliente_id": id_cliente,
            "productos": [{"producto_id": id_usb, "cantidad": 999}]
        }, headers=headers_cliente)

        assert resp.status_code == 400
        error = resp.get_json()
        assert "error" in error
        assert "stock" in str(error).lower()

        # Verificar que el stock NO se modifico
        stock_usb = client.get(f"/api/productos/{id_usb}").get_json()["stock"]
        assert stock_usb == 30

    def test_cliente_no_puede_ver_reporte(self, client):
        """
        SEGURIDAD: un cliente NO debe poder ver los reportes de ventas.
        Solo el rol admin tiene acceso.
        """
        token_cliente = self._crear_cliente(client)
        headers_cliente = {"Authorization": f"Bearer {token_cliente}"}

        resp = client.get("/api/reportes/ventas", headers=headers_cliente)
        assert resp.status_code == 403

    def test_busqueda_productos(self, client):
        """Buscar productos por nombre retorna solo los que coinciden."""
        token_admin = self._crear_admin(client)
        headers_admin = {"Authorization": f"Bearer {token_admin}"}
        self._crear_productos(client, headers_admin, sufijo="C")

        resp = client.get("/api/productos/?buscar=mouse")
        assert resp.status_code == 200
        productos = resp.get_json()["productos"]
        assert len(productos) >= 1
        assert all("ouse" in p["nombre"].lower() for p in productos)

    def test_sku_duplicado_retorna_409(self, client):
        """Crear dos productos con el mismo SKU debe retornar 409."""
        token_admin = self._crear_admin(client)
        headers_admin = {"Authorization": f"Bearer {token_admin}"}
        self._crear_productos(client, headers_admin, sufijo="D")

        resp = client.post("/api/productos/", json={
            "sku": "LAPD001",
            "nombre": "Otra Laptop",
            "precio": 9999.00,
            "stock": 5
        }, headers=headers_admin)