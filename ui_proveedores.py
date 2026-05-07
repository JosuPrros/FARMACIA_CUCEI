import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager
import ui_registro_proveedor
import facturacion

COLOR_FONDO = "#F4F6F9"
COLOR_PRIMARIO = "#003B73"
COLOR_SECUNDARIO = "#00A4E4"
COLOR_EXITO = "#28A745"
COLOR_BLANCO = "#FFFFFF"

class VentanaEditarProveedor(ctk.CTkToplevel):
    def __init__(self, master, id_prov, empresa, contacto, correo, telefono):
        super().__init__(master)
        self.title("Editar Proveedor")
        self.geometry("450x550")
        self.configure(fg_color=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self.resizable(False, False)
        
        self.id_prov = id_prov
        
        self.marco_form = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=15)
        self.marco_form.pack(padx=30, pady=30, fill="both", expand=True)
        
        self.etiqueta_titulo = ctk.CTkLabel(self.marco_form, text="Editar Proveedor", font=("Helvetica", 22, "bold"), text_color=COLOR_PRIMARIO)
        self.etiqueta_titulo.pack(pady=(20, 20))
        
        self.entrada_empresa = ctk.CTkEntry(self.marco_form, height=45, corner_radius=10, border_color=COLOR_SECUNDARIO)
        self.entrada_empresa.pack(pady=(0, 15), padx=30, fill="x")
        self.entrada_empresa.insert(0, str(empresa))
        
        self.entrada_contacto = ctk.CTkEntry(self.marco_form, placeholder_text="Contacto", height=45, corner_radius=10, border_color=COLOR_SECUNDARIO)
        self.entrada_contacto.pack(pady=(0, 15), padx=30, fill="x")
        if contacto and contacto != "None": self.entrada_contacto.insert(0, str(contacto))
        
        self.entrada_correo = ctk.CTkEntry(self.marco_form, placeholder_text="Correo", height=45, corner_radius=10, border_color=COLOR_SECUNDARIO)
        self.entrada_correo.pack(pady=(0, 15), padx=30, fill="x")
        if correo and correo != "None": self.entrada_correo.insert(0, str(correo))
        
        self.entrada_telefono = ctk.CTkEntry(self.marco_form, placeholder_text="Teléfono", height=45, corner_radius=10, border_color=COLOR_SECUNDARIO)
        self.entrada_telefono.pack(pady=(0, 25), padx=30, fill="x")
        if telefono and telefono != "None": self.entrada_telefono.insert(0, str(telefono))
        
        self.boton_guardar = ctk.CTkButton(
            self.marco_form, text="Guardar Cambios", height=50, fg_color=COLOR_EXITO, hover_color="#218838",
            font=("Helvetica", 16, "bold"), corner_radius=10, command=self.guardar_cambios
        )
        self.boton_guardar.pack(pady=(0, 20), padx=30, fill="x")
        
    def guardar_cambios(self):
        empresa = self.entrada_empresa.get()
        contacto = self.entrada_contacto.get()
        correo = self.entrada_correo.get()
        telefono = self.entrada_telefono.get()
        
        if not empresa or not contacto:
            messagebox.showwarning("Incompleto", "Empresa y contacto son obligatorios.")
            return
            
        exito, msg = db_manager.actualizar_proveedor(self.id_prov, empresa, contacto, correo, telefono)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

class PantallaProveedores(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLOR_FONDO)
        self.configurar_menu_superior()
        self.configurar_tabla()
        
    def configurar_menu_superior(self):
        self.marco_superior = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=15)
        self.marco_superior.pack(pady=20, padx=25, fill="x")
        
        self.boton_nuevo_proveedor = ctk.CTkButton(
            self.marco_superior, text="Registrar Proveedor", height=45, width=170,
            fg_color=COLOR_EXITO, hover_color="#218838", font=("Helvetica", 13, "bold"), corner_radius=10,
            command=self.evento_nuevo_proveedor
        )
        self.boton_nuevo_proveedor.pack(side="right", padx=(10, 20), pady=20)
        
        self.boton_editar_proveedor = ctk.CTkButton(
            self.marco_superior, text="Editar Proveedor", height=45, width=150,
            fg_color="#f0ad4e", hover_color="#ec971f", font=("Helvetica", 13, "bold"), corner_radius=10,
            command=self.evento_editar_proveedor
        )
        self.boton_editar_proveedor.pack(side="right", padx=(10, 0), pady=20)

        self.boton_eliminar_proveedor = ctk.CTkButton(
            self.marco_superior, text="Dar de baja", height=45, width=150,
            fg_color="#d9534f", hover_color="#c9302c", font=("Helvetica", 13, "bold"), corner_radius=10,
            command=self.evento_eliminar_proveedor
        )
        self.boton_eliminar_proveedor.pack(side="right", padx=(20, 0), pady=20)
        
    def configurar_tabla(self):
        self.marco_tabla = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=15)
        self.marco_tabla.pack(pady=(0, 20), padx=25, fill="both", expand=True)
        
        self.etiqueta_tabla = ctk.CTkLabel(self.marco_tabla, text="Directorio de Proveedores", font=("Helvetica", 18, "bold"), text_color=COLOR_PRIMARIO)
        self.etiqueta_tabla.pack(anchor="w", pady=(20, 10), padx=25)
        
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", background="#FFFFFF", rowheight=30, borderwidth=0)
        estilo.configure("Treeview.Heading", background=COLOR_PRIMARIO, foreground="white", padding=5, font=("Helvetica", 11, "bold"))
        estilo.map("Treeview", background=[("selected", COLOR_SECUNDARIO)])
        
        columnas = ("id_prov", "empresa", "contacto", "correo", "telefono")
        self.tabla = ttk.Treeview(self.marco_tabla, columns=columnas, show="headings", style="Treeview")
        
        self.tabla.heading("id_prov", text="ID")
        self.tabla.heading("empresa", text="Empresa")
        self.tabla.heading("contacto", text="Contacto")
        self.tabla.heading("correo", text="Correo Electrónico")
        self.tabla.heading("telefono", text="Teléfono")
        
        self.tabla.column("id_prov", width=50, anchor="center")
        self.tabla.column("empresa", width=250)
        self.tabla.column("contacto", width=200)
        self.tabla.column("correo", width=200)
        self.tabla.column("telefono", width=150)
        
        self.tabla.pack(pady=10, padx=25, fill="both", expand=True)
        self.cargar_datos()
        
    def cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        proveedores = db_manager.obtener_proveedores_completo()
        for p in proveedores:
            self.tabla.insert("", "end", values=p)
            
    def evento_nuevo_proveedor(self):
        ventana_nuevo = ui_registro_proveedor.PantallaRegistroProveedor(self)
        self.wait_window(ventana_nuevo)
        self.cargar_datos()
        
    def evento_editar_proveedor(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un proveedor de la tabla para editar.")
            return
            
        item = self.tabla.item(seleccion[0])
        val = item['values']
        ventana_editar = VentanaEditarProveedor(self, val[0], val[1], val[2], val[3], val[4])
        self.wait_window(ventana_editar)
        self.cargar_datos()

    def evento_eliminar_proveedor(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un proveedor para dar de baja.")
            return
            
        item = self.tabla.item(seleccion[0])
        id_prov = item['values'][0]
        empresa = item['values'][1]
        
        r1 = messagebox.askyesno("Confirmar Baja", f"¿Deseas eliminar a {empresa}?\n(Paso 1 de 3)")
        if not r1: return
        
        exito, msg, fuerza_req = db_manager.eliminar_proveedor_seguro(id_prov)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargar_datos()
        else:
            if fuerza_req:
                r2 = messagebox.askyesno("ALERTA", f"ALERTA: {msg}\n\nDejará productos sin proveedor. ¿Seguro?\n(Paso 2 de 3)")
                if not r2: return
                
                r3 = messagebox.askyesno("ÚLTIMA ADVERTENCIA", "Esta acción es irreversible. Se generará un reporte de eliminación. ¿Proceder?\n(Paso 3 de 3)")
                if not r3: return
                
                productos = db_manager.obtener_productos_por_proveedor(id_prov)
                ex_f, msg_f = db_manager.eliminar_proveedor_forzado(id_prov)
                if ex_f:
                    facturacion.generar_reporte_proveedor_eliminado(empresa, productos)
                    messagebox.showinfo("Éxito", "Proveedor eliminado forzosamente. Reporte generado.")
                    self.cargar_datos()
                else:
                    messagebox.showerror("Error", msg_f)
            else:
                messagebox.showerror("Error", msg)
