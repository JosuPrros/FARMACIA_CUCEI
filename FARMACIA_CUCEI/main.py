import customtkinter as ctk

# Importar los módulos refactorizados a CTkFrame
from ui_usuarios import PantallaUsuarios
from ui_clientes import PantallaClientes
from ui_productos import PantallaProductos
from ui_ventas import PantallaVentas
from ui_compras import PantallaCompras

# --- COLORES (Idénticos al estilo institucional) ---
COLOR_FONDO = "#F4F6F9"
COLOR_PRIMARIO = "#003B73"
COLOR_SECUNDARIO = "#00A4E4"
COLOR_BLANCO = "#FFFFFF"

ctk.set_appearance_mode("Light")

class PantallaPrincipal(ctk.CTk):
    def __init__(self, rol_usuario="Admin", nombre_usuario="Usuario"):
        super().__init__()
        
        self.rol_usuario = rol_usuario
        self.nombre_usuario = nombre_usuario
        
        self.title("Farmacia CUCEI - Dashboard Principal")
        self.geometry("1400x800")
        self.configure(fg_color=COLOR_FONDO)
        
        # --- Pantalla Completa ---
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))
        
        # Grid para el layout: 1 col para el sidebar, 1 para el centro
        self.grid_columnconfigure(0, weight=0) # Sidebar fijo
        self.grid_columnconfigure(1, weight=1) # Centro expandible
        self.grid_rowconfigure(0, weight=1)    # Toma todo el alto
        
        self.frame_actual = None
        
        self.dibujar_sidebar()
        self.dibujar_area_central()
        
        # Carga la Bienvenida por defecto
        self.mostrar_bienvenida()
        
    def dibujar_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=COLOR_PRIMARIO, corner_radius=0, width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Logo o Título Superior
        self.etiqueta_logo = ctk.CTkLabel(
            self.sidebar, text="FARMACIA\nCUCEI", 
            font=("Helvetica", 24, "bold"), text_color=COLOR_BLANCO
        )
        self.etiqueta_logo.pack(pady=(40, 50))
        
        # Botones de Navegación
        self.boton_ventas = self.crear_boton_menu("Ventas", self.abrir_ventas)
        self.boton_productos = self.crear_boton_menu("Productos", self.abrir_productos)
        self.boton_clientes = self.crear_boton_menu("Clientes", self.abrir_clientes)
        
        if self.rol_usuario in ["Admin", "Gerente"]:
            self.boton_compras = self.crear_boton_menu("Compras", self.abrir_compras)
            
        if self.rol_usuario == "Admin":
            self.boton_usuarios = self.crear_boton_menu("Usuarios", self.abrir_usuarios)
        
        # Información del empleado inyectada al fondo
        texto_empleado = f"👤 {self.nombre_usuario}\n({self.rol_usuario})\nv. 1.0"
        self.etiqueta_empleado = ctk.CTkLabel(
            self.sidebar, text=texto_empleado, 
            font=("Helvetica", 12), text_color="#A9CCEA"
        )
        self.etiqueta_empleado.pack(side="bottom", pady=20)
        
    def crear_boton_menu(self, texto, comando):
        # Función auxiliar para estandarizar los botones del menú lateral
        btn = ctk.CTkButton(
            self.sidebar, text=texto, height=50, width=200,
            font=("Helvetica", 15, "bold"), fg_color="transparent", text_color=COLOR_BLANCO,
            hover_color=COLOR_SECUNDARIO, anchor="w", command=comando
        )
        btn.pack(pady=10, padx=25)
        return btn
        
    def dibujar_area_central(self):
        self.area_central = ctk.CTkFrame(self, fg_color=COLOR_FONDO, corner_radius=0)
        self.area_central.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
    def limpiar_area_central(self):
        """Elimina la pantalla actual del área principal antes de inyectar una nueva."""
        if self.frame_actual is not None:
            self.frame_actual.destroy()
            
    def mostrar_bienvenida(self):
        self.limpiar_area_central()
        self.frame_actual = ctk.CTkFrame(self.area_central, fg_color=COLOR_BLANCO, corner_radius=20)
        self.frame_actual.pack(fill="both", expand=True)
        
        bienvenida = ctk.CTkLabel(
            self.frame_actual, text="¡Bienvenido a Farmacia CUCEI!",
            font=("Helvetica", 32, "bold"), text_color=COLOR_PRIMARIO
        )
        bienvenida.pack(expand=True)
        
    # --- FUNCIONES DE LLAMADA A MÓDULOS ---
    def abrir_ventas(self):
        self.limpiar_area_central()
        self.frame_actual = PantallaVentas(self.area_central)
        self.frame_actual.pack(fill="both", expand=True)
        
    def abrir_productos(self):
        self.limpiar_area_central()
        self.frame_actual = PantallaProductos(self.area_central)
        self.frame_actual.pack(fill="both", expand=True)
        
    def abrir_clientes(self):
        self.limpiar_area_central()
        self.frame_actual = PantallaClientes(self.area_central)
        self.frame_actual.pack(fill="both", expand=True)
        
    def abrir_compras(self):
        self.limpiar_area_central()
        self.frame_actual = PantallaCompras(self.area_central)
        self.frame_actual.pack(fill="both", expand=True)
        
    def abrir_usuarios(self):
        self.limpiar_area_central()
        self.frame_actual = PantallaUsuarios(self.area_central)
        self.frame_actual.pack(fill="both", expand=True)

if __name__ == "__main__":
    # Redirigir al inicio de sesión si se ejecuta este archivo directamente
    import ui_login
    app_login = ui_login.PantallaLogin()
    app_login.mainloop()
