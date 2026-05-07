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

class PantallaProductos(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
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
            self.marco_superior, text="Registrar Producto", height=45, width=200,
            fg_color=COLOR_EXITO, hover_color="#218838", 
            font=("Helvetica", 14, "bold"), corner_radius=10,
            command=self.evento_nuevo_producto
        )
        self.boton_nuevo_producto.pack(side="right", padx=20, pady=20)
        
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

# --- Ejecución Independiente ---
if __name__ == "__main__":
    raiz = ctk.CTk()
    raiz.title("Farmacia CUCEI - Catálogo y Control de Medicamentos")
    raiz.geometry("1100x650")
    app_productos = PantallaProductos(raiz)
    app_productos.pack(fill="both", expand=True)
    raiz.mainloop()
