import mysql.connector
from mysql.connector import Error
import hashlib

_db_initialized = False

def inicializar_esquema(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM Productos LIKE 'id_proveedor'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Productos ADD COLUMN id_proveedor INT DEFAULT NULL")
            try:
                cursor.execute("ALTER TABLE Productos ADD CONSTRAINT fk_prod_prov FOREIGN KEY (id_proveedor) REFERENCES Proveedores(id_proveedor) ON DELETE SET NULL ON UPDATE CASCADE")
            except:
                pass
            conn.commit()
            
        cursor.execute("SHOW COLUMNS FROM Compras LIKE 'id_proveedor'")
        col = cursor.fetchone()
        if col and col[2] == 'NO': # NO indicates NOT NULL
            try:
                cursor.execute("ALTER TABLE Compras DROP FOREIGN KEY compras_ibfk_1")
                cursor.execute("ALTER TABLE Compras MODIFY id_proveedor INT DEFAULT NULL")
                cursor.execute("ALTER TABLE Compras ADD CONSTRAINT compras_ibfk_1 FOREIGN KEY (id_proveedor) REFERENCES Proveedores(id_proveedor) ON DELETE SET NULL ON UPDATE CASCADE")
                conn.commit()
            except Exception as e:
                pass
                
        cursor.execute("SHOW COLUMNS FROM Detalle_Ventas LIKE 'id_producto'")
        col_dv = cursor.fetchone()
        if col_dv and col_dv[2] == 'NO':
            try:
                cursor.execute("ALTER TABLE Detalle_Ventas DROP FOREIGN KEY detalle_ventas_ibfk_2")
                cursor.execute("ALTER TABLE Detalle_Ventas MODIFY id_producto INT DEFAULT NULL")
                cursor.execute("ALTER TABLE Detalle_Ventas ADD CONSTRAINT detalle_ventas_ibfk_2 FOREIGN KEY (id_producto) REFERENCES Productos(id_producto) ON DELETE SET NULL ON UPDATE CASCADE")
                conn.commit()
            except Exception: pass
            
        cursor.execute("SHOW COLUMNS FROM Detalle_Compras LIKE 'id_producto'")
        col_dc = cursor.fetchone()
        if col_dc and col_dc[2] == 'NO':
            try:
                cursor.execute("ALTER TABLE Detalle_Compras DROP FOREIGN KEY detalle_compras_ibfk_2")
                cursor.execute("ALTER TABLE Detalle_Compras MODIFY id_producto INT DEFAULT NULL")
                cursor.execute("ALTER TABLE Detalle_Compras ADD CONSTRAINT detalle_compras_ibfk_2 FOREIGN KEY (id_producto) REFERENCES Productos(id_producto) ON DELETE SET NULL ON UPDATE CASCADE")
                conn.commit()
            except Exception: pass
            
    except Exception as e:
        print(f"[ADVERTENCIA] Error inicializando esquema: {e}")

def get_connection():
    """Establece conexión a la base de datos MySQL en XAMPP."""
    global _db_initialized
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Contraseña por defecto de XAMPP
            database='farmacia_cucei'
        )
        if conn.is_connected():
            if not _db_initialized:
                inicializar_esquema(conn)
                _db_initialized = True
            return conn
    except Error as e:
        print(f"[ERROR] No se pudo conectar a MySQL: {e}")
        return None

def hash_password(password):
    """Genera un hash SHA-256 para contraseñas de forma segura."""
    return hashlib.sha256(password.encode()).hexdigest()

# === FUNCIONES DE ACCESO A DATOS (CRUD) ===

def login(usuario_nombre_o_correo, contrasena):
    """Valida credenciales de acceso. Devuelve (id, nombre, rol) o None."""
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()
    pwd_hash = hash_password(contrasena)
    cursor.execute("""
        SELECT u.id_usuario, u.nombre_completo, r.nombre_rol 
        FROM Usuarios u 
        JOIN Roles r ON u.id_rol = r.id_rol 
        WHERE (u.correo = %s OR u.nombre_completo = %s) AND u.contrasena_hash = %s
    """, (usuario_nombre_o_correo, usuario_nombre_o_correo, pwd_hash))
    result = cursor.fetchone()
    conn.close()
    return result

# --- USUARIOS ---
def crear_usuario(nombre, correo, contrasena, rol_nombre):
    conn = get_connection()
    if not conn: return False, "Sin conexión a Base de Datos"
    cursor = conn.cursor()
    try:
        # Obtener id de rol ignorando mayúsculas/minúsculas
        cursor.execute("SELECT id_rol FROM Roles WHERE LOWER(nombre_rol) = LOWER(%s)", (rol_nombre.strip(),))
        rol_row = cursor.fetchone()
        if not rol_row: return False, "Rol no válido. Debe ser Admin, Gerente, Encargado o Cajero."
        id_rol = rol_row[0]
        
        pwd_hash = hash_password(contrasena)
        cursor.execute("INSERT INTO Usuarios (nombre_completo, correo, contrasena_hash, id_rol) VALUES (%s, %s, %s, %s)",
                       (nombre.strip(), correo.strip(), pwd_hash, id_rol))
        conn.commit()
        return True, "Usuario creado exitosamente"
    except Error as e:
        return False, f"Error en BD: {str(e)}"
    finally:
        if conn: conn.close()

def obtener_usuarios():
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id_usuario, u.nombre_completo, u.correo, r.nombre_rol 
        FROM Usuarios u JOIN Roles r ON u.id_rol = r.id_rol
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- CLIENTES ---
def crear_cliente(telefono, rfc, nombre, fecha_nac, correo):
    conn = get_connection()
    if not conn: return False, "Sin conexión a Base de Datos"
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Clientes (telefono, rfc_cliente, nombre_completo, fecha_nacimiento, correo) VALUES (%s, %s, %s, %s, %s)",
                       (telefono, rfc, nombre, fecha_nac, correo))
        conn.commit()
        return True, "Cliente registrado"
    except Error as e:
        return False, f"Error en BD: {str(e)}"
    finally:
        if conn: conn.close()

def obtener_clientes():
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT telefono, rfc_cliente, nombre_completo, fecha_nacimiento, puntos_acumulados FROM Clientes")
    rows = cursor.fetchall()
    conn.close()
    return rows

def eliminar_cliente(telefono):
    conn = get_connection()
    if not conn: return False, "Sin conexión a Base de Datos"
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Clientes WHERE telefono = %s", (telefono,))
        conn.commit()
        return True, "Cliente eliminado exitosamente"
    except Error as e:
        if "foreign key constraint" in str(e).lower():
            return False, "No se puede eliminar el cliente porque tiene ventas asociadas."
        return False, f"Error en BD: {str(e)}"
    finally:
        if conn: conn.close()

def obtener_puntos_cliente(telefono):
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()
    cursor.execute("SELECT puntos_acumulados FROM Clientes WHERE telefono = %s", (telefono,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def obtener_datos_facturacion(telefono):
    conn = get_connection()
    if not conn: return None, None, None
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_completo, correo, rfc_cliente FROM Clientes WHERE telefono = %s", (telefono,))
    row = cursor.fetchone()
    conn.close()
    return (row[0], row[1], row[2]) if row else (None, None, None)

# --- PROVEEDORES ---
def crear_proveedor(empresa, contacto, correo, telefono):
    conn = get_connection()
    if not conn: return False, "Sin conexión a Base de Datos"
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Proveedores (nombre_empresa, nombre_contacto, correo, telefono) VALUES (%s, %s, %s, %s)",
                       (empresa, contacto, correo, telefono))
        conn.commit()
        return True, "Proveedor registrado"
    except Error as e:
        return False, f"Error en BD: {str(e)}"
    finally:
        if conn: conn.close()

def obtener_proveedores():
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id_proveedor, nombre_empresa FROM Proveedores")
    rows = cursor.fetchall()
    conn.close()
    return rows

def obtener_proveedores_completo():
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id_proveedor, nombre_empresa, nombre_contacto, correo, telefono FROM Proveedores")
    rows = cursor.fetchall()
    conn.close()
    return rows

def obtener_datos_proveedor(id_proveedor):
    conn = get_connection()
    if not conn: return None, None
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_empresa, correo FROM Proveedores WHERE id_proveedor = %s", (id_proveedor,))
    row = cursor.fetchone()
    conn.close()
    return (row[0], row[1]) if row else (None, None)

def obtener_productos_por_proveedor(id_proveedor):
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_comercial FROM Productos WHERE id_proveedor = %s", (id_proveedor,))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def actualizar_proveedor(id_proveedor, empresa, contacto, correo, telefono):
    conn = get_connection()
    if not conn: return False, "Sin conexión a BD"
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Proveedores 
            SET nombre_empresa = %s, nombre_contacto = %s, correo = %s, telefono = %s 
            WHERE id_proveedor = %s
        """, (empresa, contacto, correo, telefono, id_proveedor))
        conn.commit()
        return True, "Proveedor actualizado correctamente"
    except Error as e:
        return False, f"Error: {e}"
    finally:
        if conn: conn.close()

def eliminar_proveedor_seguro(id_proveedor):
    conn = get_connection()
    if not conn: return False, "Sin conexión a BD", False
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Proveedores WHERE id_proveedor = %s", (id_proveedor,))
        conn.commit()
        return True, "Proveedor eliminado exitosamente", False
    except Error as e:
        if "foreign key constraint" in str(e).lower():
            return False, "Tiene historial. Requiere fuerza.", True
        return False, f"Error: {e}", False
    finally:
        if conn: conn.close()

def eliminar_proveedor_forzado(id_proveedor):
    conn = get_connection()
    if not conn: return False, "Sin conexión a BD"
    cursor = conn.cursor()
    try:
        # Con ON DELETE SET NULL se actualizarán las tablas hijas automáticamente.
        cursor.execute("DELETE FROM Proveedores WHERE id_proveedor = %s", (id_proveedor,))
        conn.commit()
        return True, "Proveedor eliminado forzosamente"
    except Error as e:
        return False, f"Error: {e}"
    finally:
        if conn: conn.close()

# --- PRODUCTOS / INVENTARIO ---
def obtener_productos():
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id_producto, p.nombre_comercial, c.nombre_clasificacion, p.precio_publico, p.stock_fisico 
        FROM Productos p JOIN Clasificaciones c ON p.id_clasificacion = c.id_clasificacion
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def buscar_producto(termino):
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    query = f"%{termino}%"
    cursor.execute("""
        SELECT p.id_producto, p.nombre_comercial, c.nombre_clasificacion, p.precio_publico, p.stock_fisico 
        FROM Productos p JOIN Clasificaciones c ON p.id_clasificacion = c.id_clasificacion
        WHERE p.id_producto LIKE %s OR p.nombre_comercial LIKE %s
    """, (query, query))
    rows = cursor.fetchall()
    conn.close()
    return rows

def obtener_proveedor_de_producto(termino):
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()
    query = f"%{termino}%"
    cursor.execute("""
        SELECT p.id_producto, p.nombre_comercial, p.id_proveedor
        FROM Productos p
        WHERE p.id_producto LIKE %s OR p.nombre_comercial LIKE %s
        LIMIT 1
    """, (query, query))
    row = cursor.fetchone()
    conn.close()
    return row

def obtener_clasificaciones():
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id_clasificacion, nombre_clasificacion FROM Clasificaciones")
    rows = cursor.fetchall()
    
    if not rows:
        try:
            cursor.execute("INSERT INTO Clasificaciones (nombre_clasificacion) VALUES ('General')")
            conn.commit()
            cursor.execute("SELECT id_clasificacion, nombre_clasificacion FROM Clasificaciones")
            rows = cursor.fetchall()
        except Error:
            pass
            
    conn.close()
    return rows

def registrar_producto_completo(nombre_comercial, id_clasificacion, id_proveedor, precio, stock_fisico):
    conn = get_connection()
    if not conn: return False, "Sin conexión a Base de Datos"
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Productos (nombre_comercial, id_clasificacion, id_proveedor, precio_publico, stock_fisico) VALUES (%s, %s, %s, %s, %s)",
                       (nombre_comercial.strip(), id_clasificacion, id_proveedor, precio, stock_fisico))
        conn.commit()
        return True, "Producto registrado correctamente en la base de datos."
    except Error as e:
        return False, f"Error en BD: {str(e)}"
    finally:
        if conn: conn.close()

def registrar_producto_basico(nombre_comercial, precio):
    # Por retrocompatibilidad con scripts de prueba
    return registrar_producto_completo(nombre_comercial, 1, None, precio, 0)

def eliminar_producto_seguro(id_producto):
    conn = get_connection()
    if not conn: return False, "Sin conexión a Base de Datos", False
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Productos WHERE id_producto = %s", (id_producto,))
        conn.commit()
        return True, "Producto eliminado exitosamente", False
    except Error as e:
        if "foreign key constraint" in str(e).lower():
            return False, "No se puede eliminar el producto porque tiene compras o ventas asociadas.", True
        return False, f"Error en BD: {str(e)}", False
    finally:
        if conn: conn.close()

def eliminar_producto_forzado(id_producto):
    conn = get_connection()
    if not conn: return False, "Sin conexión a BD"
    cursor = conn.cursor()
    try:
        # Con ON DELETE SET NULL se actualizarán las tablas hijas automáticamente.
        cursor.execute("DELETE FROM Productos WHERE id_producto = %s", (id_producto,))
        conn.commit()
        return True, "Producto eliminado forzosamente"
    except Error as e:
        return False, f"Error: {e}"
    finally:
        if conn: conn.close()

def actualizar_producto(id_producto, nombre_comercial, precio_publico, id_proveedor):
    conn = get_connection()
    if not conn: return False, "Sin conexión a Base de Datos"
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Productos 
            SET nombre_comercial = %s, precio_publico = %s, id_proveedor = %s 
            WHERE id_producto = %s
        """, (nombre_comercial.strip(), precio_publico, id_proveedor, id_producto))
        conn.commit()
        return True, "Producto actualizado correctamente."
    except Error as e:
        return False, f"Error en BD: {str(e)}"
    finally:
        if conn: conn.close()

# --- COMPRAS (Abastecimiento) ---
def registrar_compra(id_proveedor, id_usuario, costo_total, items):
    conn = get_connection()
    if not conn: return False, "Sin conexión a Base de Datos"
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Compras (id_proveedor, id_usuario_registro, costo_total_factura) VALUES (%s, %s, %s)",
                       (id_proveedor, id_usuario, costo_total))
        id_compra = cursor.lastrowid
        
        for id_prod, nombre_med, cant, subtot in items:
            cursor.execute("SELECT id_producto FROM Productos WHERE id_producto = %s", (id_prod,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO Productos (id_producto, nombre_comercial, id_clasificacion, precio_publico, stock_fisico) VALUES (%s, %s, %s, %s, %s)",
                               (id_prod, nombre_med, 1, 0.0, 0))
            
            cursor.execute("INSERT INTO Detalle_Compras (id_compra, id_producto, cantidad_piezas, costo_subtotal) VALUES (%s, %s, %s, %s)",
                           (id_compra, id_prod, cant, subtot))
                           
            cursor.execute("UPDATE Productos SET stock_fisico = stock_fisico + %s WHERE id_producto = %s",
                           (cant, id_prod))
        conn.commit()
        return True, "Compra registrada y stock actualizado"
    except Error as e:
        conn.rollback()
        return False, f"Error: {str(e)}"
    finally:
        if conn: conn.close()

# --- VENTAS ---
def registrar_venta(id_usuario, telefono_cliente, total, descuento_usado, puntos_generados, items):
    conn = get_connection()
    if not conn: return False, "Sin conexión a Base de Datos"
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Ventas (id_usuario_cajero, telefono_cliente, total_venta, puntos_generados) VALUES (%s, %s, %s, %s)",
                       (id_usuario, telefono_cliente, total, puntos_generados))
        id_venta = cursor.lastrowid
        
        for item in items:
            id_prod, cant, prec, subt = item[0], item[1], item[2], item[3]
            cursor.execute("INSERT INTO Detalle_Ventas (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                           (id_venta, id_prod, cant, prec, subt))
                           
            cursor.execute("UPDATE Productos SET stock_fisico = stock_fisico - %s WHERE id_producto = %s",
                           (cant, id_prod))
                           
        if telefono_cliente:
            if descuento_usado:
                cursor.execute("UPDATE Clientes SET puntos_acumulados = 0 WHERE telefono = %s", (telefono_cliente,))
            else:
                cursor.execute("UPDATE Clientes SET puntos_acumulados = puntos_acumulados + %s WHERE telefono = %s", (puntos_generados, telefono_cliente))
        
        conn.commit()
        return True, "Venta concretada correctamente"
    except Error as e:
        conn.rollback()
        return False, f"Error en venta: {str(e)}"
    finally:
        if conn: conn.close()

# --- TURNOS / REPORTES ---
def obtener_ventas_periodo(inicio, fin):
    conn = get_connection()
    if not conn: return 0.0
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total_venta) FROM Ventas WHERE fecha_venta BETWEEN %s AND %s", (inicio, fin))
    row = cursor.fetchone()
    conn.close()
    return float(row[0]) if row and row[0] else 0.0

def obtener_compras_periodo(inicio, fin):
    conn = get_connection()
    if not conn: return 0.0
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(costo_total_factura) FROM Compras WHERE fecha_compra BETWEEN %s AND %s", (inicio, fin))
    row = cursor.fetchone()
    conn.close()
    return float(row[0]) if row and row[0] else 0.0

def obtener_producto_mas_vendido(inicio, fin):
    conn = get_connection()
    if not conn: return "N/A"
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.nombre_comercial, SUM(dv.cantidad) as total_vendido
        FROM Detalle_Ventas dv
        JOIN Ventas v ON dv.id_venta = v.id_venta
        JOIN Productos p ON dv.id_producto = p.id_producto
        WHERE v.fecha_venta BETWEEN %s AND %s
        GROUP BY dv.id_producto
        ORDER BY total_vendido DESC
        LIMIT 1
    """, (inicio, fin))
    row = cursor.fetchone()
    conn.close()
    return f"{row[0]} ({int(row[1])} pz)" if row else "Ninguno"


# === MENÚ INTERACTIVO DE PRUEBAS ===
if __name__ == "__main__":
    while True:
        print("\n" + "="*40)
        print("MENÚ DE PRUEBAS: BASE DE DATOS")
        print("="*40)
        print("1. Añadir Usuario")
        print("2. Añadir Cliente")
        print("3. Añadir Proveedor")
        print("4. Añadir Producto")
        print("5. Salir")
        opcion = input("Elige una opción: ")
        
        match opcion:
            case "1":
                print("\n--- NUEVO USUARIO ---")
                nombre = input("Nombre completo: ")
                correo = input("Correo (Login): ")
                contra = input("Contraseña: ")
                rol = input("Rol (Admin/Gerente/Encargado/Cajero): ")
                exito, msg = crear_usuario(nombre, correo, contra, rol)
                print(f"-> {msg}")
                
            case "2":
                print("\n--- NUEVO CLIENTE ---")
                rfc = input("RFC: ")
                nombre = input("Nombre completo: ")
                fecha = input("Fecha de Nacimiento (AAAA-MM-DD): ")
                correo = input("Correo: ")
                exito, msg = crear_cliente(rfc, nombre, fecha, correo)
                print(f"-> {msg}")
                
            case "3":
                print("\n--- NUEVO PROVEEDOR ---")
                empresa = input("Nombre de la Empresa: ")
                contacto = input("Nombre del Contacto: ")
                correo = input("Correo: ")
                telefono = input("Teléfono: ")
                exito, msg = crear_proveedor(empresa, contacto, correo, telefono)
                print(f"-> {msg}")
                
            case "4":
                print("\n--- NUEVO PRODUCTO ---")
                nombre = input("Nombre comercial: ")
                precio = input("Precio al público: ")
                try:
                    exito, msg = registrar_producto_basico(nombre, float(precio))
                    print(f"-> {msg}")
                except ValueError:
                    print("-> Error: El precio debe ser un número.")
                
            case "5":
                print("Saliendo del menú de pruebas...")
                break
                
            case _:
                print("-> Opción no válida. Intenta de nuevo.")
