import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager

# --- COLORES (Farmacias Similares) ---
COLOR_FONDO = "#F4F6F9"
COLOR_PRIMARIO = "#003B73"
COLOR_SECUNDARIO = "#00A4E4"
COLOR_BLANCO = "#FFFFFF"

# Configuración del framework
ctk.set_appearance_mode("Light")

class PantallaUsuarios(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # --- Configuración Básica del Marco ---
        self.configure(fg_color=COLOR_FONDO)
        
        # Dividir la pantalla principal en 2 columnas: 
        # Columna 0: Formulario (más pequeña)
        # Columna 1: Tabla (más grande)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # Llamamos a los métodos que dibujan cada parte de la pantalla
        self.dibujar_area_formulario()
        self.dibujar_area_tabla()
        
    def dibujar_area_formulario(self):
        """Dibuja el panel izquierdo dedicado a registrar nuevos usuarios."""
        
        # Marco del formulario (Fondo blanco, tipo panel lateral)
        self.marco_formulario = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=20)
        self.marco_formulario.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Título
        self.etiqueta_titulo = ctk.CTkLabel(
            self.marco_formulario, 
            text="Alta de Usuario", 
            font=("Helvetica", 22, "bold"), 
            text_color=COLOR_PRIMARIO
        )
        self.etiqueta_titulo.pack(pady=(30, 20))
        
        # Campos de texto correspondientes a los atributos del Usuario
        self.entrada_nombre_completo = ctk.CTkEntry(
            self.marco_formulario, 
            placeholder_text="Nombre Completo", 
            height=45, 
            corner_radius=10,
            border_color=COLOR_SECUNDARIO
        )
        self.entrada_nombre_completo.pack(pady=10, padx=30, fill="x")
        
        self.entrada_usuario = ctk.CTkEntry(
            self.marco_formulario, 
            placeholder_text="Usuario o Correo", 
            height=45, 
            corner_radius=10,
            border_color=COLOR_SECUNDARIO
        )
        self.entrada_usuario.pack(pady=10, padx=30, fill="x")
        
        self.entrada_contrasena = ctk.CTkEntry(
            self.marco_formulario, 
            placeholder_text="Contraseña", 
            show="*",
            height=45, 
            corner_radius=10,
            border_color=COLOR_SECUNDARIO
        )
        self.entrada_contrasena.pack(pady=10, padx=30, fill="x")
        
        # Combobox para el Rol
        self.variable_rol = ctk.StringVar(value="Seleccionar Rol")
        self.combo_rol = ctk.CTkComboBox(
            self.marco_formulario,
            values=["Admin", "Gerente", "Encargado"],
            variable=self.variable_rol,
            height=45,
            corner_radius=10,
            border_color=COLOR_SECUNDARIO,
            button_color=COLOR_PRIMARIO,
            button_hover_color=COLOR_SECUNDARIO,
            state="readonly"
        )
        self.combo_rol.pack(pady=10, padx=30, fill="x")
        
        # Botón para Guardar Datos
        self.boton_guardar_usuario = ctk.CTkButton(
            self.marco_formulario, 
            text="GUARDAR USUARIO", 
            height=50,
            font=("Helvetica", 14, "bold"), 
            fg_color=COLOR_PRIMARIO, 
            hover_color=COLOR_SECUNDARIO, 
            corner_radius=15, 
            command=self.evento_guardar_usuario
        )
        self.boton_guardar_usuario.pack(pady=(40, 20), padx=30, fill="x")
        
        # Botón para Limpiar (Estilo secundario)
        self.boton_limpiar = ctk.CTkButton(
            self.marco_formulario, 
            text="Limpiar Formulario", 
            height=40,
            font=("Helvetica", 12), 
            fg_color="gray", 
            hover_color="#555555", 
            corner_radius=10, 
            command=self.evento_limpiar_campos
        )
        self.boton_limpiar.pack(pady=0, padx=30, fill="x")

    def dibujar_area_tabla(self):
        """Dibuja el panel derecho que muestra todos los usuarios registrados."""
        
        # Marco para la tabla (Fondo blanco)
        self.marco_tabla = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=20)
        self.marco_tabla.grid(row=0, column=1, padx=(0,20), pady=20, sticky="nsew")
        
        # Área superior de la tabla (Título y buscador)
        self.marco_busqueda = ctk.CTkFrame(self.marco_tabla, fg_color="transparent")
        self.marco_busqueda.pack(fill="x", pady=20, padx=30)
        
        self.etiqueta_tabla = ctk.CTkLabel(
            self.marco_busqueda, 
            text="Padrón de Usuarios", 
            font=("Helvetica", 22, "bold"), 
            text_color=COLOR_PRIMARIO
        )
        self.etiqueta_tabla.pack(side="left")
        
        self.entrada_buscar = ctk.CTkEntry(
            self.marco_busqueda, 
            placeholder_text="Buscar por nombre o usuario...",
            width=250, height=35, corner_radius=8
        )
        self.entrada_buscar.pack(side="right", padx=(10,0))
        
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", background="#FFFFFF", foreground="black", rowheight=30, fieldbackground="#FFFFFF", borderwidth=0)
        estilo.configure("Treeview.Heading", background=COLOR_PRIMARIO, foreground="white", font=("Helvetica", 11, "bold"), padding=[0, 8])
        estilo.map("Treeview", background=[("selected", COLOR_SECUNDARIO)])
        
        columnas_tabla = ("id", "nombre", "usuario", "rol")
        self.tabla_usuarios = ttk.Treeview(self.marco_tabla, columns=columnas_tabla, show="headings", style="Treeview")
        
        self.tabla_usuarios.heading("id", text="ID")
        self.tabla_usuarios.heading("nombre", text="Nombre Completo")
        self.tabla_usuarios.heading("usuario", text="Usuario / Correo")
        self.tabla_usuarios.heading("rol", text="Rol")
        
        self.tabla_usuarios.column("id", width=50, anchor="center")
        self.tabla_usuarios.column("nombre", width=250)
        self.tabla_usuarios.column("usuario", width=150)
        self.tabla_usuarios.column("rol", width=100, anchor="center")
        
        self.tabla_usuarios.pack(pady=(0, 20), padx=30, fill="both", expand=True)
        
        self.cargar_datos()
        
    def cargar_datos(self):
        # Limpiar tabla
        for item in self.tabla_usuarios.get_children():
            self.tabla_usuarios.delete(item)
            
        # Cargar desde DB
        usuarios = db_manager.obtener_usuarios()
        for u in usuarios:
            self.tabla_usuarios.insert("", "end", values=u)
        
    def evento_guardar_usuario(self):
        nombre = self.entrada_nombre_completo.get()
        usuario = self.entrada_usuario.get()
        contrasena = self.entrada_contrasena.get()
        rol = self.combo_rol.get()
        
        if not nombre or not usuario or not contrasena or rol == "Seleccionar Rol":
            messagebox.showwarning("Campos Incompletos", "Por favor completa todos los campos para registrar al usuario.")
            return
            
        exito, msg = db_manager.crear_usuario(nombre, usuario, contrasena, rol)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.evento_limpiar_campos()
            self.cargar_datos()
        else:
            messagebox.showerror("Error", msg)
        
    def evento_limpiar_campos(self):
        self.entrada_nombre_completo.delete(0, "end")
        self.entrada_usuario.delete(0, "end")
        self.entrada_contrasena.delete(0, "end")
        self.combo_rol.set("Seleccionar Rol")
        print("[INFO] Formulario de usuarios limpiado.")

# --- Ejecución Independiente ---
if __name__ == "__main__":
    raiz = ctk.CTk()
    raiz.title("Farmacia CUCEI - Módulo de Usuarios")
    raiz.geometry("1000x650")
    app_usuarios = PantallaUsuarios(raiz)
    app_usuarios.pack(fill="both", expand=True)
    raiz.mainloop()
