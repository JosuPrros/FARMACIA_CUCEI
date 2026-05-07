import customtkinter as ctk
from tkinter import messagebox
import db_manager

# --- COLORES ---
COLOR_FONDO = "#F4F6F9"
COLOR_PRIMARIO = "#003B73"
COLOR_SECUNDARIO = "#00A4E4"
COLOR_EXITO = "#28A745"
COLOR_BLANCO = "#FFFFFF"

class VentanaNuevoProducto(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        
        self.title("Registrar Nuevo Producto")
        self.geometry("450x550")
        self.configure(fg_color=COLOR_FONDO)
        
        # Centrar la ventana respecto al padre si existe
        if master:
            self.transient(master)
        self.grab_set()
        
        # Desactivar redimensionamiento y no utilizar pantalla completa
        self.resizable(False, False)
        
        self.crear_formulario()
        
    def crear_formulario(self):
        self.marco_form = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=15)
        self.marco_form.pack(padx=30, pady=30, fill="both", expand=True)
        
        self.etiqueta_titulo = ctk.CTkLabel(
            self.marco_form, text="Datos del Producto", 
            font=("Helvetica", 22, "bold"), text_color=COLOR_PRIMARIO
        )
        self.etiqueta_titulo.pack(pady=(20, 20))
        
        # 1. Nombre Comercial
        self.entrada_nombre = ctk.CTkEntry(
            self.marco_form, placeholder_text="Nombre Comercial", 
            height=45, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_nombre.pack(pady=(0, 15), padx=30, fill="x")
        
        # 2. Clasificación
        clasificaciones = db_manager.obtener_clasificaciones()
        # Si no hay clasificaciones (base de datos vacía o sin inicializar), proveer un fallback.
        self.nombres_clasificaciones = [c[1] for c in clasificaciones] if clasificaciones else ["General"]
        self.mapa_clasificaciones = {c[1]: c[0] for c in clasificaciones} if clasificaciones else {"General": 1}
        
        self.combo_clasificacion = ctk.CTkComboBox(
            self.marco_form, values=self.nombres_clasificaciones,
            height=45, corner_radius=10, border_color=COLOR_SECUNDARIO,
            state="readonly"
        )
        self.combo_clasificacion.pack(pady=(0, 15), padx=30, fill="x")
        self.combo_clasificacion.set(self.nombres_clasificaciones[0])
        
        # 3. Precio al Público
        self.entrada_precio = ctk.CTkEntry(
            self.marco_form, placeholder_text="Precio al Público (Ej. 150.50)", 
            height=45, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_precio.pack(pady=(0, 15), padx=30, fill="x")
        
        # 4. Stock Físico Inicial
        self.entrada_stock = ctk.CTkEntry(
            self.marco_form, placeholder_text="Stock Inicial (Ej. 0)", 
            height=45, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_stock.pack(pady=(0, 25), padx=30, fill="x")
        
        self.boton_guardar = ctk.CTkButton(
            self.marco_form, text="Guardar Producto", height=50,
            fg_color=COLOR_EXITO, hover_color="#218838",
            font=("Helvetica", 16, "bold"), corner_radius=10,
            command=self.guardar_producto
        )
        self.boton_guardar.pack(pady=(0, 20), padx=30, fill="x")
        
    def guardar_producto(self):
        nombre = self.entrada_nombre.get()
        clasificacion_nombre = self.combo_clasificacion.get()
        precio_str = self.entrada_precio.get()
        stock_str = self.entrada_stock.get()
        
        if not nombre or not precio_str or clasificacion_nombre == "":
            messagebox.showwarning("Campos incompletos", "Por favor llena los campos Nombre y Precio.")
            return
            
        try:
            precio = float(precio_str)
            stock = int(stock_str) if stock_str else 0
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser numérico y el stock debe ser un número entero.")
            return
            
        id_clasificacion = self.mapa_clasificaciones.get(clasificacion_nombre, 1)
        
        exito, msg = db_manager.registrar_producto_completo(nombre, id_clasificacion, precio, stock)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

# Para pruebas unitarias
if __name__ == "__main__":
    raiz = ctk.CTk()
    app = VentanaNuevoProducto(raiz)
    raiz.mainloop()
