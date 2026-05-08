import customtkinter as ctk
from tkinter import ttk, messagebox
import datetime
import db_manager

# --- COLORES (Farmacias Similares) ---
COLOR_FONDO = "#F4F6F9"
COLOR_PRIMARIO = "#003B73"
COLOR_SECUNDARIO = "#00A4E4"
COLOR_BLANCO = "#FFFFFF"

# Configuración del framework
ctk.set_appearance_mode("Light")

class PantallaClientes(ctk.CTkFrame):
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
        """Dibuja el panel izquierdo dedicado a registrar nuevos clientes."""
        
        # Marco del formulario (Fondo blanco, tipo panel lateral)
        self.marco_formulario = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=20)
        self.marco_formulario.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Título
        self.etiqueta_titulo = ctk.CTkLabel(
            self.marco_formulario, 
            text="Alta de Cliente", 
            font=("Helvetica", 22, "bold"), 
            text_color=COLOR_PRIMARIO
        )
        self.etiqueta_titulo.pack(pady=(30, 20))
        
        # Campos de texto correspondientes a los atributos del Cliente
        self.entrada_nombre_completo = ctk.CTkEntry(
            self.marco_formulario, 
            placeholder_text="Nombre Completo del Cliente", 
            height=45, 
            corner_radius=10,
            border_color=COLOR_SECUNDARIO
        )
        self.entrada_nombre_completo.pack(pady=10, padx=30, fill="x")
        
        self.entrada_telefono = ctk.CTkEntry(
            self.marco_formulario, 
            placeholder_text="Teléfono (10 dígitos)", 
            height=45, 
            corner_radius=10,
            border_color=COLOR_SECUNDARIO
        )
        self.entrada_telefono.pack(pady=10, padx=30, fill="x")
        
        self.entrada_rfc = ctk.CTkEntry(
            self.marco_formulario, 
            placeholder_text="RFC del Cliente", 
            height=45, 
            corner_radius=10,
            border_color=COLOR_SECUNDARIO
        )
        self.entrada_rfc.pack(pady=10, padx=30, fill="x")
        
        self.entrada_correo = ctk.CTkEntry(
            self.marco_formulario, 
            placeholder_text="Correo electrónico", 
            height=45, 
            corner_radius=10,
            border_color=COLOR_SECUNDARIO
        )
        self.entrada_correo.pack(pady=10, padx=30, fill="x")
        
        # Marco para la fecha de nacimiento usando Comboboxes
        self.marco_fecha = ctk.CTkFrame(self.marco_formulario, fg_color="transparent")
        self.marco_fecha.pack(pady=10, padx=30, fill="x")
        
        anio_actual = datetime.datetime.now().year
        dias = [str(i).zfill(2) for i in range(1, 32)]
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        anios = [str(i) for i in range(anio_actual, 1900, -1)]
        
        self.combo_dia = ctk.CTkComboBox(self.marco_fecha, values=dias, corner_radius=10, border_color=COLOR_SECUNDARIO)
        self.combo_dia.pack(side="left", padx=(0, 5), expand=True, fill="x")
        self.combo_dia.set("Día")
        
        self.combo_mes = ctk.CTkComboBox(self.marco_fecha, values=meses, corner_radius=10, border_color=COLOR_SECUNDARIO)
        self.combo_mes.pack(side="left", padx=5, expand=True, fill="x")
        self.combo_mes.set("Mes")
        
        self.combo_anio = ctk.CTkComboBox(self.marco_fecha, values=anios, corner_radius=10, border_color=COLOR_SECUNDARIO)
        self.combo_anio.pack(side="left", padx=(5, 0), expand=True, fill="x")
        self.combo_anio.set("Año")
        
        # Botón para Guardar Datos
        self.boton_guardar_cliente = ctk.CTkButton(
            self.marco_formulario, 
            text="GUARDAR CLIENTE", 
            height=50,
            font=("Helvetica", 14, "bold"), 
            fg_color=COLOR_PRIMARIO, 
            hover_color=COLOR_SECUNDARIO, 
            corner_radius=15, 
            command=self.evento_guardar_cliente
        )
        self.boton_guardar_cliente.pack(pady=(40, 20), padx=30, fill="x")
        
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
        """Dibuja el panel derecho que muestra todos los clientes registrados."""
        
        # Marco para la tabla (Fondo blanco)
        self.marco_tabla = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=20)
        self.marco_tabla.grid(row=0, column=1, padx=(0,20), pady=20, sticky="nsew")
        
        # Área superior de la tabla (Título y buscador)
        self.marco_busqueda = ctk.CTkFrame(self.marco_tabla, fg_color="transparent")
        self.marco_busqueda.pack(fill="x", pady=20, padx=30)
        
        self.etiqueta_tabla = ctk.CTkLabel(
            self.marco_busqueda, 
            text="Padrón de Clientes / Puntos", 
            font=("Helvetica", 22, "bold"), 
            text_color=COLOR_PRIMARIO
        )
        self.etiqueta_tabla.pack(side="left")
        
        self.entrada_buscar = ctk.CTkEntry(
            self.marco_busqueda, 
            placeholder_text="Buscar por RFC...",
            width=200, height=35, corner_radius=8
        )
        self.entrada_buscar.pack(side="right", padx=(10,0))
        
        self.boton_eliminar_cliente = ctk.CTkButton(
            self.marco_busqueda,
            text="Eliminar Seleccionado",
            font=("Helvetica", 12, "bold"),
            fg_color="#D9534F",
            hover_color="#C9302C",
            width=150, height=35, corner_radius=8,
            command=self.evento_eliminar_cliente
        )
        self.boton_eliminar_cliente.pack(side="right", padx=(10, 10))
        
        # Tabla de datos usando ttk.Treeview dado que ctk no tiene tabla nativa, pero se puede estilizar
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", background="#FFFFFF", foreground="black", rowheight=30, fieldbackground="#FFFFFF", borderwidth=0)
        estilo.configure("Treeview.Heading", background=COLOR_PRIMARIO, foreground="white", font=("Helvetica", 11, "bold"), padding=[0, 8])
        estilo.map("Treeview", background=[("selected", COLOR_SECUNDARIO)])
        
        columnas_tabla = ("telefono", "rfc", "nombre", "fecha", "puntos")
        self.tabla_clientes = ttk.Treeview(self.marco_tabla, columns=columnas_tabla, show="headings", style="Treeview")
        
        self.tabla_clientes.heading("telefono", text="Teléfono")
        self.tabla_clientes.heading("rfc", text="RFC")
        self.tabla_clientes.heading("nombre", text="Nombre Completo")
        self.tabla_clientes.heading("fecha", text="Fecha de Nacimiento")
        self.tabla_clientes.heading("puntos", text="Puntos")
        
        self.tabla_clientes.column("telefono", width=120, anchor="center")
        self.tabla_clientes.column("rfc", width=120, anchor="center")
        self.tabla_clientes.column("nombre", width=250)
        self.tabla_clientes.column("fecha", width=100, anchor="center")
        self.tabla_clientes.column("puntos", width=120, anchor="center")
        
        self.tabla_clientes.pack(pady=(0, 20), padx=30, fill="both", expand=True)
        
        self.cargar_datos()
        
    def cargar_datos(self):
        for item in self.tabla_clientes.get_children():
            self.tabla_clientes.delete(item)
            
        clientes = db_manager.obtener_clientes()
        for c in clientes:
            self.tabla_clientes.insert("", "end", values=c)
            
    def evento_guardar_cliente(self):
        nombre = self.entrada_nombre_completo.get()
        telefono = self.entrada_telefono.get()
        rfc = self.entrada_rfc.get()
        correo = self.entrada_correo.get() if hasattr(self, "entrada_correo") else ""
        dia = self.combo_dia.get()
        mes = self.combo_mes.get()
        anio = self.combo_anio.get()
        
        if not nombre or not telefono or dia == "Día" or mes == "Mes" or anio == "Año":
            messagebox.showwarning("Campos Incompletos", "Por favor completa el nombre, Teléfono y fecha de nacimiento.")
            return
            
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        mes_num = str(meses.index(mes) + 1).zfill(2)
        fecha_nac = f"{anio}-{mes_num}-{dia.zfill(2)}"
        
        exito, msg = db_manager.crear_cliente(telefono, rfc, nombre, fecha_nac, correo)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.evento_limpiar_campos()
            self.cargar_datos()
        else:
            messagebox.showerror("Error", msg)
        
    def evento_limpiar_campos(self):
        self.entrada_nombre_completo.delete(0, "end")
        self.entrada_telefono.delete(0, "end")
        self.entrada_rfc.delete(0, "end")
        if hasattr(self, "entrada_correo"):
            self.entrada_correo.delete(0, "end")
        self.combo_dia.set("Día")
        self.combo_mes.set("Mes")
        self.combo_anio.set("Año")
        print("[INFO] Formulario de clientes limpiado.")

    def evento_eliminar_cliente(self):
        seleccion = self.tabla_clientes.selection()
        if not seleccion:
            messagebox.showwarning("Selección Requerida", "Por favor, selecciona un cliente de la tabla para eliminar.")
            return
            
        item = self.tabla_clientes.item(seleccion[0])
        telefono = item['values'][0] # Teléfono is the first column
        nombre = item['values'][2] # Nombre is the third column
        
        confirmacion = messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que deseas eliminar al cliente {nombre} (Tel: {telefono})?")
        if confirmacion:
            exito, msg = db_manager.eliminar_cliente(str(telefono))
            if exito:
                messagebox.showinfo("Éxito", msg)
                self.cargar_datos()
            else:
                messagebox.showerror("Error", msg)

# --- Ejecución Independiente ---
if __name__ == "__main__":
    raiz = ctk.CTk()
    raiz.title("Farmacia CUCEI - Módulo de Clientes")
    raiz.geometry("1000x650")
    app_clientes = PantallaClientes(raiz)
    app_clientes.pack(fill="both", expand=True)
    raiz.mainloop()
