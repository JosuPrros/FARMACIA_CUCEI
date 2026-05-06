import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager

# --- COLORES ---
COLOR_FONDO = "#F4F6F9"
COLOR_PRIMARIO = "#003B73"
COLOR_SECUNDARIO = "#00A4E4"
COLOR_BLANCO = "#FFFFFF"

ctk.set_appearance_mode("Light")

class PantallaCompras(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color=COLOR_FONDO)
        
        # Una columna, múltiples filas (1 para el formulario, otra para el grid de la orden)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Fila superior estática (Form)
        self.grid_rowconfigure(1, weight=1) # Fila inferior responsiva (Tabla)
        
        self.crear_formulario_recepcion()
        self.crear_orden_cargada()
        
    def crear_formulario_recepcion(self):
        """Bloque Blanco Superior donde el gerente mete los datos a registrar de la compra de lote."""
        self.marco_formulario = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=15)
        self.marco_formulario.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="nsew")
        
        # Título
        self.etiqueta_titulo = ctk.CTkLabel(
            self.marco_formulario, text="Carga de Lotes (Nuevo Inventario)", 
            font=("Helvetica", 20, "bold"), text_color=COLOR_PRIMARIO
        )
        self.etiqueta_titulo.grid(row=0, column=0, columnspan=3, pady=(20, 15), padx=25, sticky="w")
        
        # Botón Registrar Proveedor
        self.boton_registrar_proveedor = ctk.CTkButton(
            self.marco_formulario, text="📝 Registrar Proveedor", height=35,
            fg_color=COLOR_PRIMARIO, hover_color=COLOR_SECUNDARIO, font=("Helvetica", 12, "bold"),
            corner_radius=8, command=self.evento_registrar_proveedor
        )
        self.boton_registrar_proveedor.grid(row=0, column=3, columnspan=2, padx=(10, 25), pady=(20, 15), sticky="e")
        
        # P1: Proveedor
        self.entrada_proveedor = ctk.CTkEntry(
            self.marco_formulario, placeholder_text="ID Proveedor (Ej. 1)", 
            height=45, width=200, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_proveedor.grid(row=1, column=0, padx=(25, 10), pady=(0, 20), sticky="w")
        
        # P2: Medicamento
        self.entrada_medicamento = ctk.CTkEntry(
            self.marco_formulario, placeholder_text="ID Producto (Ej. P01)", 
            height=45, width=230, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_medicamento.grid(row=1, column=1, padx=10, pady=(0, 20), sticky="w")
        
        # P3: Cantidad de piezas a ingresar
        self.entrada_piezas = ctk.CTkEntry(
            self.marco_formulario, placeholder_text="Cantidad...", 
            height=45, width=150, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_piezas.grid(row=1, column=2, padx=10, pady=(0, 20), sticky="w")

        # P4: Costo Total Factura (Para estadísticas de Gerente)
        self.entrada_costo = ctk.CTkEntry(
            self.marco_formulario, placeholder_text="Costo Factura ($)", 
            height=45, width=150, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_costo.grid(row=1, column=3, padx=10, pady=(0, 20), sticky="w")
        
        # Botón para añadir registro "temporal" a la lista de captura antes de oficializar
        self.boton_agregar_lista = ctk.CTkButton(
            self.marco_formulario, text="➕ Agregar", height=45, 
            fg_color=COLOR_SECUNDARIO, hover_color=COLOR_PRIMARIO, font=("Helvetica", 13, "bold"),
            corner_radius=10, command=self.evento_agregar_linea
        )
        self.boton_agregar_lista.grid(row=1, column=4, padx=(10, 25), pady=(0, 20), sticky="e")
        
    def crear_orden_cargada(self):
        """Bloque Blanco Inferior donde se va mostrando toda la línea de captura del remonte entrante y botón Confirmar Gral."""
        self.marco_tabla = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=15)
        self.marco_tabla.grid(row=1, column=0, padx=25, pady=(10, 25), sticky="nsew")
        
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", background="#FFFFFF", rowheight=30, borderwidth=0)
        estilo.configure("Treeview.Heading", background=COLOR_PRIMARIO, foreground="white", font=("Helvetica", 11, "bold"), padding=5)
        
        columnas = ("proveedor", "medicamento", "piezas", "costo_total")
        self.tabla_ingresos = ttk.Treeview(self.marco_tabla, columns=columnas, show="headings", style="Treeview")
        
        self.tabla_ingresos.heading("proveedor", text="Proveedor Comercial")
        self.tabla_ingresos.heading("medicamento", text="Medicamento Recibido")
        self.tabla_ingresos.heading("piezas", text="Unidades Ingresadas (+ Stock)")
        self.tabla_ingresos.heading("costo_total", text="Gasto Carga")
        
        self.tabla_ingresos.column("proveedor", width=200)
        self.tabla_ingresos.column("medicamento", width=250)
        self.tabla_ingresos.column("piezas", width=200, anchor="center")
        self.tabla_ingresos.column("costo_total", width=150, anchor="e")
        
        self.tabla_ingresos.pack(pady=(25,10), padx=25, fill="both", expand=True)
        
        # FINALIZAR CARGA GLOBAL (Aplica a DB directa por Gerente)
        self.boton_confirmar_stock = ctk.CTkButton(
            self.marco_tabla, text="CONFIRMAR ENTRADAS Y ACTUALIZAR STOCK EN DB", 
            height=60, font=("Helvetica", 16, "bold"), 
            fg_color=COLOR_PRIMARIO, hover_color="#002142", corner_radius=15, 
            command=self.evento_confirmar_stock_global
        )
        self.boton_confirmar_stock.pack(side="bottom", pady=25, padx=25, fill="x")

    def evento_agregar_linea(self):
        proveedor = self.entrada_proveedor.get()
        med = self.entrada_medicamento.get()
        piezas = self.entrada_piezas.get()
        costo = self.entrada_costo.get()
        
        if not proveedor or not med or not piezas or not costo:
            messagebox.showwarning("Incompleto", "Llena todos los campos para agregar a la lista.")
            return
            
        self.tabla_ingresos.insert("", "end", values=(proveedor, med, piezas, f"${costo}"))
        
        # Limpiar los de producto
        self.entrada_medicamento.delete(0, "end")
        self.entrada_piezas.delete(0, "end")
        
    def evento_registrar_proveedor(self):
        # Importar y mostrar la nueva ventana popup para registro
        from ui_registro_proveedor import PantallaRegistroProveedor
        ventana_registro = PantallaRegistroProveedor(master=self.winfo_toplevel())
        
    def evento_confirmar_stock_global(self):
        items = []
        for child in self.tabla_ingresos.get_children():
            val = self.tabla_ingresos.item(child)["values"]
            # val = [id_proveedor, id_producto, cantidad, costo_string]
            costo_num = float(str(val[3]).replace("$", ""))
            items.append((str(val[1]), "Producto Recibido", int(val[2]), costo_num))
            
        if not items:
            messagebox.showinfo("Vacío", "No hay elementos para procesar.")
            return
            
        # Tomar proveedor del primer elemento y costo total sumado o del input
        id_prov = int(self.tabla_ingresos.item(self.tabla_ingresos.get_children()[0])["values"][0])
        costo_total = float(self.entrada_costo.get()) if self.entrada_costo.get() else sum([i[3] for i in items])
        id_usuario = 1 # Para simplificar la demostración, usamos el ID 1 por defecto
        
        exito, msg = db_manager.registrar_compra(id_prov, id_usuario, costo_total, items)
        if exito:
            messagebox.showinfo("Éxito", msg)
            for item in self.tabla_ingresos.get_children():
                self.tabla_ingresos.delete(item)
            self.entrada_proveedor.delete(0, "end")
            self.entrada_costo.delete(0, "end")
        else:
            messagebox.showerror("Error", msg)

# --- Ejecución Independiente ---
if __name__ == "__main__":
    raiz = ctk.CTk()
    raiz.title("Farmacia CUCEI - Recepción y Compras a Proveedores")
    raiz.geometry("1100x650")
    app_compras = PantallaCompras(raiz)
    app_compras.pack(fill="both", expand=True)
    raiz.mainloop()
