import customtkinter as ctk
from tkinter import messagebox
import db_manager

# --- COLORES ---
COLOR_FONDO = "#F4F6F9"
COLOR_PRIMARIO = "#003B73"
COLOR_SECUNDARIO = "#00A4E4"
COLOR_BLANCO = "#FFFFFF"

class PantallaRegistroProveedor(ctk.CTkToplevel):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.title("Registrar Nuevo Proveedor")
        self.geometry("500x600")
        self.configure(fg_color=COLOR_FONDO)
        
        # Centrar la ventana respecto al padre si existe, si no en la pantalla
        if master:
            self.transient(master) # Mantenerla siempre encima del padre
        self.grab_set() # Hacerla modal para que el usuario deba completarla
        
        # --- Pantalla Completa ---
        self.attributes("-fullscreen", False)
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))
        
        self.crear_formulario()
        
    def crear_formulario(self):
        self.marco_formulario = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=15)
        self.marco_formulario.pack(padx=30, pady=30, fill="both", expand=True)
        
        # Título
        self.etiqueta_titulo = ctk.CTkLabel(
            self.marco_formulario, text="Datos del Proveedor", 
            font=("Helvetica", 22, "bold"), text_color=COLOR_PRIMARIO
        )
        self.etiqueta_titulo.pack(pady=(20, 30))
        
        # Nombre de la empresa
        self.entrada_empresa = ctk.CTkEntry(
            self.marco_formulario, placeholder_text="Nombre de la Empresa", 
            height=45, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_empresa.pack(pady=10, padx=40, fill="x")
        
        # Nombre del proveedor (contacto)
        self.entrada_contacto = ctk.CTkEntry(
            self.marco_formulario, placeholder_text="Nombre del Contacto (Proveedor)", 
            height=45, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_contacto.pack(pady=10, padx=40, fill="x")
        
        # Correo electrónico
        self.entrada_correo = ctk.CTkEntry(
            self.marco_formulario, placeholder_text="Correo Electrónico", 
            height=45, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_correo.pack(pady=10, padx=40, fill="x")
        
        # Teléfono
        self.entrada_telefono = ctk.CTkEntry(
            self.marco_formulario, placeholder_text="Teléfono", 
            height=45, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_telefono.pack(pady=10, padx=40, fill="x")
        
        # Botón Guardar
        self.boton_guardar = ctk.CTkButton(
            self.marco_formulario, text="GUARDAR PROVEEDOR", 
            height=50, font=("Helvetica", 14, "bold"), 
            fg_color=COLOR_PRIMARIO, hover_color=COLOR_SECUNDARIO, corner_radius=15, 
            command=self.evento_guardar
        )
        self.boton_guardar.pack(pady=(30, 10), padx=40, fill="x")
        
        # Botón Cancelar
        self.boton_cancelar = ctk.CTkButton(
            self.marco_formulario, text="Cancelar", 
            height=40, font=("Helvetica", 12), 
            fg_color="gray", hover_color="#555555", corner_radius=10, 
            command=self.destroy
        )
        self.boton_cancelar.pack(pady=10, padx=40, fill="x")
        
    def evento_guardar(self):
        empresa = self.entrada_empresa.get()
        contacto = self.entrada_contacto.get()
        correo = self.entrada_correo.get()
        telefono = self.entrada_telefono.get()
        
        if not empresa or not contacto:
            messagebox.showwarning("Incompleto", "Nombre de empresa y contacto son obligatorios.")
            return
            
        exito, msg = db_manager.crear_proveedor(empresa, contacto, correo, telefono)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    # Para probar este archivo de forma independiente
    app = ctk.CTk()
    app.geometry("0x0") # Ocultamos la ventana principal para ver solo el Toplevel
    ventana = PantallaRegistroProveedor(app)
    app.mainloop()
