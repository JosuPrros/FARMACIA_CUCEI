import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager
import ui_registro_producto

# --- COLORES ---
COLOR_FONDO = "#F4F6F9"
COLOR_PRIMARIO = "#003B73"
COLOR_SECUNDARIO = "#00A4E4"
COLOR_EXITO = "#28A745" # Un verde bandera ligero para el boton de agregar
COLOR_BLANCO = "#FFFFFF"

ctk.set_appearance_mode("Light")

class VentanaEditarProducto(ctk.CTkToplevel):
    def __init__(self, master, id_producto, nombre_actual, precio_actual, id_prov_actual):
        super().__init__(master)
        
        self.title("Editar Producto")
        self.geometry("450x450")
        self.configure(fg_color=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self.resizable(False, False)
        
        self.id_producto = id_producto
        
        self.marco_form = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=15)
        self.marco_form.pack(padx=30, pady=30, fill="both", expand=True)
        
        self.etiqueta_titulo = ctk.CTkLabel(
            self.marco_form, text="Editar Producto", 
            font=("Helvetica", 22, "bold"), text_color=COLOR_PRIMARIO
        )
        self.etiqueta_titulo.pack(pady=(20, 20))
        
        self.entrada_nombre = ctk.CTkEntry(self.marco_form, height=45, corner_radius=10, border_color=COLOR_SECUNDARIO)
        self.entrada_nombre.pack(pady=(0, 15), padx=30, fill="x")
        self.entrada_nombre.insert(0, nombre_actual)
        
        self.entrada_proveedor = ctk.CTkEntry(self.marco_form, placeholder_text="ID Proveedor", height=45, corner_radius=10, border_color=COLOR_SECUNDARIO)
        self.entrada_proveedor.pack(pady=(0, 15), padx=30, fill="x")
        if id_prov_actual:
            self.entrada_proveedor.insert(0, str(id_prov_actual))
            
        precio_limpio = str(precio_actual).replace("$", "")
        self.entrada_precio = ctk.CTkEntry(self.marco_form, placeholder_text="Precio Público", height=45, corner_radius=10, border_color=COLOR_SECUNDARIO)
        self.entrada_precio.pack(pady=(0, 25), padx=30, fill="x")
        self.entrada_precio.insert(0, precio_limpio)
        
        self.boton_guardar = ctk.CTkButton(
            self.marco_form, text="Guardar Cambios", height=50,
            fg_color=COLOR_EXITO, hover_color="#218838",
            font=("Helvetica", 16, "bold"), corner_radius=10,
            command=self.guardar_cambios
        )
        self.boton_guardar.pack(pady=(0, 20), padx=30, fill="x")
        
    def guardar_cambios(self):
        nombre = self.entrada_nombre.get()
        prov_str = self.entrada_proveedor.get()
        precio_str = self.entrada_precio.get()
        
        if not nombre or not prov_str or not precio_str:
            messagebox.showwarning("Incompleto", "Llena todos los campos.")
            return
            
        try:
            precio = float(precio_str)
            id_prov = int(prov_str)
        except ValueError:
            messagebox.showerror("Error", "Precio y ID Proveedor deben ser numéricos.")
            return
            
        # Validar existencia del proveedor
        nombre_prov, _ = db_manager.obtener_datos_proveedor(id_prov)
        if nombre_prov is None:
            messagebox.showerror("Error", f"El proveedor con ID {id_prov} no existe.")
            return
            
        exito, msg = db_manager.actualizar_producto(self.id_producto, nombre, precio, id_prov)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

class PantallaProductos(ctk.CTkFrame):
    def __init__(self, master=None, rol="Admin", **kwargs):
        super().__init__(master, **kwargs)
        self.rol = rol
        
        self.configure(fg_color=COLOR_FONDO)
        
        # Área superior: Buscador y Acciones Generales (Nuevo Producto, etc.)
        self.configurar_menu_superior()
        # Área Principal: Tabla general de inventario
        self.configurar_tabla()
        
    def configurar_menu_superior(self):
        """Barra blanca superior que contiene control de filtros y botones principales"""
        self.marco_superior = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=15)
        self.marco_superior.pack(pady=20, padx=25, fill="x")
        
        # Input de "Buscar"
        self.entrada_buscar = ctk.CTkEntry(
            self.marco_superior, 
            placeholder_text=" Buscar medicamento por nombre o código...", 
            width=350, height=45, corner_radius=10,
            border_color=COLOR_SECUNDARIO
        )
        self.entrada_buscar.pack(side="left", padx=20, pady=20)
        
        # Botón Buscar
        self.boton_buscar = ctk.CTkButton(
            self.marco_superior, text="Buscar", height=45, width=120,
            fg_color=COLOR_PRIMARIO, hover_color=COLOR_SECUNDARIO, 
            font=("Helvetica", 14), corner_radius=10, command=self.evento_buscar
        )
        self.boton_buscar.pack(side="left", padx=5)

        # Botón Nuevo Producto (Gerente)
        self.boton_nuevo_producto = ctk.CTkButton(
            self.marco_superior, text="Registrar Producto", height=45, width=170,
            fg_color=COLOR_EXITO, hover_color="#218838", 
            font=("Helvetica", 13, "bold"), corner_radius=10,
            command=self.evento_nuevo_producto
        )
        
        # Botón Editar Producto
        self.boton_editar_producto = ctk.CTkButton(
            self.marco_superior, text="Editar Producto", height=45, width=150,
            fg_color="#f0ad4e", hover_color="#ec971f", 
            font=("Helvetica", 13, "bold"), corner_radius=10,
            command=self.evento_editar_producto
        )

        # Botón Dar de baja Producto
        self.boton_eliminar_producto = ctk.CTkButton(
            self.marco_superior, text="Dar de baja producto", height=45, width=170,
            fg_color="#d9534f", hover_color="#c9302c", 
            font=("Helvetica", 13, "bold"), corner_radius=10,
            command=self.evento_eliminar_producto
        )

        if self.rol in ["Admin", "Gerente"]:
            self.boton_eliminar_producto.pack(side="right", padx=(20, 0), pady=20)
            self.boton_editar_producto.pack(side="right", padx=(10, 0), pady=20)
            self.boton_nuevo_producto.pack(side="right", padx=(10, 0), pady=20)
        
    def configurar_tabla(self):
        """Dibuja un frame con una tabla (Treeview) para mostrar todo el stock de forma ordenada"""
        self.marco_tabla = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=15)
        self.marco_tabla.pack(pady=(0, 20), padx=25, fill="both", expand=True)
        
        # Label informativo
        self.etiqueta_tabla = ctk.CTkLabel(
            self.marco_tabla, text="Inventario de Productos / Stock", 
            font=("Helvetica", 18, "bold"), text_color=COLOR_PRIMARIO
        )
        self.etiqueta_tabla.pack(anchor="w", pady=(20, 10), padx=25)
        
        # Configuramos los estilos del Treeview de Tkinter para fusionarlo con CustomTkinter
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", background="#FFFFFF", rowheight=30, borderwidth=0)
        estilo.configure("Treeview.Heading", background=COLOR_PRIMARIO, foreground="white", padding=5, font=("Helvetica", 11, "bold"))
        estilo.map("Treeview", background=[("selected", COLOR_SECUNDARIO)])
        
        columnas = ("id_med", "nombre", "clasificacion", "precio", "stock")
        self.tabla_medicamentos = ttk.Treeview(self.marco_tabla, columns=columnas, show="headings", style="Treeview")
        
        # Cabeceras
        self.tabla_medicamentos.heading("id_med", text="ID / Código")
        self.tabla_medicamentos.heading("nombre", text="Nombre Comercial")
        self.tabla_medicamentos.heading("clasificacion", text="Clasificación")
        self.tabla_medicamentos.heading("precio", text="Precio al Público")
        self.tabla_medicamentos.heading("stock", text="Stock Físico")
        
        # Tamaños
        self.tabla_medicamentos.column("id_med", width=100, anchor="center")
        self.tabla_medicamentos.column("nombre", width=350)
        self.tabla_medicamentos.column("clasificacion", width=200, anchor="center")
        self.tabla_medicamentos.column("precio", width=150, anchor="e")
        self.tabla_medicamentos.column("stock", width=100, anchor="center")
        
        self.tabla_medicamentos.pack(pady=10, padx=25, fill="both", expand=True)
        
        self.cargar_datos()
        
    def cargar_datos(self):
        for item in self.tabla_medicamentos.get_children():
            self.tabla_medicamentos.delete(item)
            
        productos = db_manager.obtener_productos()
        for p in productos:
            # Formatear el precio
            p_format = list(p)
            p_format[3] = f"${p[3]:.2f}"
            self.tabla_medicamentos.insert("", "end", values=p_format)
        
    def evento_buscar(self):
        termino = self.entrada_buscar.get()
        if not termino:
            self.cargar_datos()
            return
            
        for item in self.tabla_medicamentos.get_children():
            self.tabla_medicamentos.delete(item)
            
        productos = db_manager.buscar_producto(termino)
        for p in productos:
            p_format = list(p)
            p_format[3] = f"${p[3]:.2f}"
            self.tabla_medicamentos.insert("", "end", values=p_format)

    def evento_nuevo_producto(self):
        ventana_nuevo = ui_registro_producto.VentanaNuevoProducto(self)
        self.wait_window(ventana_nuevo) # Esperar a que se cierre para actualizar la tabla
        self.cargar_datos()

    def evento_eliminar_producto(self):
        seleccion = self.tabla_medicamentos.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor selecciona un producto de la tabla para dar de baja.")
            return
            
        item = self.tabla_medicamentos.item(seleccion[0])
        id_producto = item['values'][0]
        nombre_producto = item['values'][1]
        
        r1 = messagebox.askyesno("Confirmar Baja", f"¿Deseas eliminar el producto '{nombre_producto}'?\n(Paso 1 de 3)")
        if not r1: return
        
        exito, msg, fuerza_req = db_manager.eliminar_producto_seguro(id_producto)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargar_datos()
        else:
            if fuerza_req:
                r2 = messagebox.askyesno("ALERTA", f"ALERTA: {msg}\n\nDejará movimientos de inventario sin producto. ¿Seguro?\n(Paso 2 de 3)")
                if not r2: return
                
                r3 = messagebox.askyesno("ÚLTIMA ADVERTENCIA", "Esta acción es irreversible. Se generará un reporte de eliminación. ¿Proceder?\n(Paso 3 de 3)")
                if not r3: return
                
                info_prod = db_manager.obtener_proveedor_de_producto(id_producto)
                id_prov = info_prod[2] if info_prod else None
                nombre_prov = ""
                if id_prov:
                    nombre_prov, _ = db_manager.obtener_datos_proveedor(id_prov)
                
                ex_f, msg_f = db_manager.eliminar_producto_forzado(id_producto)
                if ex_f:
                    import facturacion
                    facturacion.generar_reporte_producto_eliminado(nombre_producto, nombre_prov)
                    messagebox.showinfo("Éxito", "Producto eliminado forzosamente. Reporte generado.")
                    self.cargar_datos()
                else:
                    messagebox.showerror("Error", msg_f)
            else:
                messagebox.showerror("Error", msg)

    def evento_editar_producto(self):
        seleccion = self.tabla_medicamentos.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor selecciona un producto de la tabla para editar.")
            return
            
        item = self.tabla_medicamentos.item(seleccion[0])
        id_producto = item['values'][0]
        nombre_producto = item['values'][1]
        precio_producto = item['values'][3]
        
        info_prod = db_manager.obtener_proveedor_de_producto(id_producto)
        id_prov = info_prod[2] if info_prod else ""
        
        ventana_editar = VentanaEditarProducto(self, id_producto, nombre_producto, precio_producto, id_prov)
        self.wait_window(ventana_editar)
        self.cargar_datos()

# --- Ejecución Independiente ---
if __name__ == "__main__":
    raiz = ctk.CTk()
    raiz.title("Farmacia CUCEI - Catálogo y Control de Medicamentos")
    raiz.geometry("1100x650")
    app_productos = PantallaProductos(raiz)
    app_productos.pack(fill="both", expand=True)
    raiz.mainloop()
