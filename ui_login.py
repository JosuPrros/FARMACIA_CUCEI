import customtkinter as ctk
import db_manager
from tkinter import messagebox

# --- CONFIGURACIÓN DE COLORES (Estilo Farmacias Similares) ---
COLOR_FONDO = "#F4F6F9"         # Gris muy claro para el fondo (limpio y médico)
COLOR_PRIMARIO = "#003B73"      # Azul oscuro corporativo principal
COLOR_SECUNDARIO = "#00A4E4"    # Azul claro/cyan (usado en logotipos de similares)
COLOR_TEXTO = "#333333"         # Gris oscuro para leer cómodamente
COLOR_BLANCO = "#FFFFFF"

# Ajustes generales para el framework
ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue") 

class PantallaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- Configuración Básica de la Ventana ---
        self.title("Farmacia CUCEI - Inicio de Sesión")
        self.geometry("450x550")
        self.configure(fg_color=COLOR_FONDO)
        self.resizable(False, False) # Desactivar maximizar ya que es un login simple
        
        # --- Pantalla Completa ---
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))
        
        # --- Marco Principal (Tarjeta de Login) ---
        # corner_radius le da el diseño moderno y bordes suaves / redondos
        self.marco_login = ctk.CTkFrame(
            self, 
            fg_color=COLOR_BLANCO, 
            corner_radius=25
        )
        # expand=True centra el marco
        self.marco_login.pack(pady=50, padx=40, fill="both", expand=True)
        
        # --- Elementos dentro de la Tarjeta ---
        
        # 1. Título
        self.etiqueta_bienvenida = ctk.CTkLabel(
            self.marco_login, 
            text="FARMACIA CUCEI", 
            font=("Helvetica", 26, "bold"),
            text_color=COLOR_PRIMARIO
        )
        self.etiqueta_bienvenida.pack(pady=(40, 10))
        
        self.etiqueta_subtitulo = ctk.CTkLabel(
            self.marco_login, 
            text="Ingrese sus credenciales de acceso", 
            font=("Helvetica", 14),
            text_color="gray"
        )
        self.etiqueta_subtitulo.pack(pady=(0, 30))
        
        # 2. Entrada de Usuario
        self.entrada_usuario = ctk.CTkEntry(
            self.marco_login, 
            placeholder_text="Usuario",
            width=280,
            height=45,
            corner_radius=12,
            border_width=2,
            border_color=COLOR_PRIMARIO,
            fg_color=COLOR_FONDO
        )
        self.entrada_usuario.pack(pady=(0, 20))
        
        # 3. Entrada de Contraseña
        self.entrada_contrasena = ctk.CTkEntry(
            self.marco_login, 
            placeholder_text="Contraseña",
            show="*", # Oculta los caracteres
            width=280,
            height=45,
            corner_radius=12,
            border_width=2,
            border_color=COLOR_PRIMARIO,
            fg_color=COLOR_FONDO
        )
        self.entrada_contrasena.pack(pady=(0, 40))
        
        # 4. Botón de Iniciar Sesión
        self.boton_ingresar = ctk.CTkButton(
            self.marco_login, 
            text="INICIAR SESIÓN",
            width=280,
            height=50,
            corner_radius=15,
            font=("Helvetica", 16, "bold"),
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_SECUNDARIO, # Efecto hover responsivo al azul claro
            command=self.evento_iniciar_sesion
        )
        self.boton_ingresar.pack(pady=(0, 30))

    def evento_iniciar_sesion(self):
        usuario_capturado = self.entrada_usuario.get()
        contrasena_capturada = self.entrada_contrasena.get()
        
        if usuario_capturado == "" or contrasena_capturada == "":
            messagebox.showwarning("Campos Vacíos", "Es necesario ingresar usuario y contraseña.")
            return
            
        print(f"[INFO] Intentando iniciar sesión con usuario: '{usuario_capturado}'")
        
        # Validación Real contra Base de Datos
        resultado = db_manager.login(usuario_capturado, contrasena_capturada)
        
        if resultado:
            id_usuario, nombre_completo, rol_asignado = resultado
            print(f"[INFO] Inicio de sesión exitoso. Bienvenido {nombre_completo} ({rol_asignado})")
            
            # Cerramos la ventana de Login
            self.destroy()
            
            # Importamos aquí para evitar dependencias circulares al cargar la app
            from ui_main import PantallaPrincipal
            
            # Abrimos el Dashboard Principal pasando el rol y nombre
            app_main = PantallaPrincipal(rol_usuario=rol_asignado, nombre_usuario=nombre_completo)
            app_main.mainloop()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas o usuario no existe.")

# --- Bloque principal para correr solo este módulo (Pruebas unitarias GUI) ---
if __name__ == "__main__":
    app_login = PantallaLogin()
    app_login.mainloop()
