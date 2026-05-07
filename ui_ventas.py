import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager
import facturacion

# --- COLORES ---
COLOR_FONDO = "#F4F6F9"
COLOR_PRIMARIO = "#003B73"
COLOR_SECUNDARIO = "#00A4E4"
COLOR_ALERTA = "#FF8C00"      # Naranja para resaltar puntos / descuentos importantes
COLOR_BOTON_COBRAR = "#28A745" # Verde potente para llamar a la acción de cobrar
COLOR_BLANCO = "#FFFFFF"

ctk.set_appearance_mode("Light")

class PantallaVentas(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color=COLOR_FONDO)
        
        # Se divide la pantalla en 2.
        # Izquierda: El carrito o Ticket (Grande). Derecha: Zona de Resumen Monetario y Cliente (Pequeña).
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.configurar_area_ticket()
        self.configurar_area_cobro()
        
    def configurar_area_ticket(self):
        self.marco_ticket = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=15)
        self.marco_ticket.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # 1. Buscador Rápido (Lector de códigos)
        self.marco_busqueda_med = ctk.CTkFrame(self.marco_ticket, fg_color="transparent")
        self.marco_busqueda_med.pack(pady=20, padx=20, fill="x")
        
        self.entrada_codigo_barras = ctk.CTkEntry(
            self.marco_busqueda_med, placeholder_text="Escanee o teclee código/nombre...", 
            height=45, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_codigo_barras.pack(side="left", fill="x", expand=True, padx=(0,10))
        
        self.entrada_cantidad = ctk.CTkEntry(
            self.marco_busqueda_med, placeholder_text="Cantidad.", width=70,
            height=45, corner_radius=10, border_color=COLOR_SECUNDARIO
        )
        self.entrada_cantidad.pack(side="left", padx=(0,10))
        self.entrada_cantidad.insert(0, "1")
        
        self.boton_agregar_cesta = ctk.CTkButton(
            self.marco_busqueda_med, text="AGREGAR", 
            height=45, width=100, font=("Helvetica", 14, "bold"), fg_color=COLOR_SECUNDARIO, hover_color=COLOR_PRIMARIO, 
            corner_radius=10, command=self.evento_agregar_cesta
        )
        self.boton_agregar_cesta.pack(side="left")
        
        self.boton_eliminar_ultimo = ctk.CTkButton(
            self.marco_busqueda_med, text="ELIMINAR", 
            height=45, width=130, font=("Helvetica", 12, "bold"), fg_color="#d9534f", hover_color="#c9302c", 
            corner_radius=10, command=self.evento_eliminar_ultimo
        )
        self.boton_eliminar_ultimo.pack(side="right", padx=(10,0))
        
        # 2. Rejilla que emula el Ticket de compra
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", background="#FFFFFF", rowheight=35, borderwidth=0, font=("Courier", 11))
        estilo.configure("Treeview.Heading", background=COLOR_PRIMARIO, foreground="white", font=("Helvetica", 11, "bold"), padding=5)
        
        columnas_ticket = ("med", "cant", "precio", "subtotal")
        self.tabla_ticket = ttk.Treeview(self.marco_ticket, columns=columnas_ticket, show="headings", style="Treeview")
        
        self.tabla_ticket.heading("med", text="Descripción Producto")
        self.tabla_ticket.heading("cant", text="Cantidad")
        self.tabla_ticket.heading("precio", text="P. Unitario")
        self.tabla_ticket.heading("subtotal", text="Subtotal")
        
        self.tabla_ticket.column("med", width=300)
        self.tabla_ticket.column("cant", width=100, anchor="center")
        self.tabla_ticket.column("precio", width=120, anchor="e")
        self.tabla_ticket.column("subtotal", width=120, anchor="e")
        
        self.tabla_ticket.pack(pady=10, padx=20, fill="both", expand=True)

    def configurar_area_cobro(self):
        self.marco_cobro = ctk.CTkFrame(self, fg_color=COLOR_BLANCO, corner_radius=15)
        self.marco_cobro.grid(row=0, column=1, padx=(0,20), pady=20, sticky="nsew")
        
        # --- BLOQUE 1: Datos de Asignación Cliente (Fidelidad) ---
        self.etiqueta_cliente = ctk.CTkLabel(
            self.marco_cobro, text="Datos del Cliente", 
            font=("Helvetica", 18, "bold"), text_color=COLOR_PRIMARIO
        )
        self.etiqueta_cliente.pack(pady=(20, 10), padx=20, anchor="w")
        
        self.entrada_telefono_venta = ctk.CTkEntry(
            self.marco_cobro, placeholder_text="Teléfono del Cliente (10 dígitos)...", height=40, corner_radius=10
        )
        self.entrada_telefono_venta.pack(pady=5, padx=20, fill="x")
        
        self.boton_verificar_cliente = ctk.CTkButton(
            self.marco_cobro, text="Checar Puntos", height=35, 
            fg_color=COLOR_PRIMARIO, hover_color=COLOR_SECUNDARIO, corner_radius=10,
            command=self.evento_verificar_puntos
        )
        self.boton_verificar_cliente.pack(pady=10, padx=20, fill="x")
        
        # Etiqueta que indicará dinámicamente si tiene promoción
        self.etiqueta_puntos_actuales = ctk.CTkLabel(
            self.marco_cobro, text="PUNTOS: -- \nSin Descuento.", 
            text_color=COLOR_ALERTA, font=("Helvetica", 13, "bold"), justify="center"
            )
        self.etiqueta_puntos_actuales.pack(pady=5)
        
        # --- BLOQUE 2: Resumen Total de Cobro ---
        self.marco_totales = ctk.CTkFrame(self.marco_cobro, fg_color=COLOR_FONDO, corner_radius=15)
        self.marco_totales.pack(pady=20, padx=20, fill="x", side="top")
        
        self.etiqueta_subtotal = ctk.CTkLabel(self.marco_totales, text="Subtotal: $0.00", font=("Helvetica", 14), text_color="#555")
        self.etiqueta_subtotal.pack(pady=(15, 5))
        
        self.etiqueta_descuento = ctk.CTkLabel(self.marco_totales, text="Descuento (Puntos): $0.00", font=("Helvetica", 14), text_color="#d9534f")
        self.etiqueta_descuento.pack(pady=5)
        
        # Total Destacado
        self.etiqueta_total_final = ctk.CTkLabel(self.marco_totales, text="TOTAL: $0.00", font=("Helvetica", 28, "bold"), text_color=COLOR_PRIMARIO)
        self.etiqueta_total_final.pack(pady=(15, 20))
        
        # GRAN BOTÓN DE PAGO FINAL
        self.boton_registrar_pago = ctk.CTkButton(
            self.marco_cobro, text="💰 COBRAR TICKET", height=65, 
            font=("Helvetica", 20, "bold"), fg_color=COLOR_BOTON_COBRAR, hover_color="#218838", 
            corner_radius=15, command=self.evento_registrar_venta
        )
        self.boton_registrar_pago.pack(side="bottom", pady=25, padx=20, fill="x")
        
    def calcular_totales(self):
        subtotal = 0.0
        for child in self.tabla_ticket.get_children():
            val = self.tabla_ticket.item(child)["values"]
            subtot_str = str(val[3]).replace("$", "")
            subtotal += float(subtot_str)
            
        self.etiqueta_subtotal.configure(text=f"Subtotal: ${subtotal:.2f}")
        
        desc_text = self.etiqueta_descuento.cget("text")
        if "10%" in desc_text:
            descuento = subtotal * 0.10
            self.etiqueta_descuento.configure(text=f"Descuento (Puntos): 10% (${descuento:.2f})")
        else:
            descuento = 0.0
            
        total = subtotal - descuento
        if total < 0: total = 0.0
        
        self.etiqueta_total_final.configure(text=f"TOTAL: ${total:.2f}")

    def evento_agregar_cesta(self):
        codigo = self.entrada_codigo_barras.get()
        cant_str = self.entrada_cantidad.get()
        if not codigo: return
        
        try:
            cant_agregar = int(cant_str)
            if cant_agregar <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero mayor a 0.")
            return
        
        res = db_manager.buscar_producto(codigo)
        if not res:
            messagebox.showwarning("No encontrado", "El producto no existe en el inventario.")
            return
            
        prod = res[0]
        id_prod, nombre, precio, stock = prod[0], prod[1], float(prod[3]), int(prod[4])
        
        # VERIFICACIÓN 1: Que el producto no esté varias veces en la tabla
        for child in self.tabla_ticket.get_children():
            val = self.tabla_ticket.item(child)["values"]
            desc_completa = str(val[0])
            id_existente = desc_completa.split("]")[0].replace("[", "")
            if id_existente == str(id_prod):
                messagebox.showwarning("Duplicado", "El producto ya está en la tabla. Si deseas cambiar la cantidad, usa el botón Eliminar Último y vuelve a agregarlo con la cantidad correcta.")
                return
        
        # VERIFICACIÓN 2: Que el stock sea el necesario
        if stock < cant_agregar:
            messagebox.showerror("Sin Stock", f"El producto {nombre} solo tiene {stock} piezas en stock disponible. No puedes añadir {cant_agregar}.")
            return
            
        subtot = precio * cant_agregar
        desc = f"[{id_prod}] {nombre}"
        self.tabla_ticket.insert("", "end", values=(desc, cant_agregar, f"${precio:.2f}", f"${subtot:.2f}"))
        self.entrada_codigo_barras.delete(0, "end")
        self.entrada_cantidad.delete(0, "end")
        self.entrada_cantidad.insert(0, "1")
        self.calcular_totales()
        
    def evento_eliminar_ultimo(self):
        items = self.tabla_ticket.get_children()
        if items:
            ultimo = items[-1]
            self.tabla_ticket.delete(ultimo)
            self.calcular_totales()
        else:
            messagebox.showwarning("Vacío", "No hay productos en la tabla para eliminar.")
        
    def evento_verificar_puntos(self):
        telefono = self.entrada_telefono_venta.get()
        if not telefono: return
        
        puntos = db_manager.obtener_puntos_cliente(telefono)
        if puntos is not None:
            if puntos >= 50:
                self.etiqueta_puntos_actuales.configure(text=f"PUNTOS: {puntos}\n¡Aplica 10% de descuento!")
                self.etiqueta_descuento.configure(text="Descuento (Puntos): 10%")
            else:
                faltan = 50 - puntos
                self.etiqueta_puntos_actuales.configure(text=f"PUNTOS: {puntos}\nFaltan {faltan} pts para el 10%.")
                self.etiqueta_descuento.configure(text="Descuento (Puntos): $0.00")
        else:
            self.etiqueta_puntos_actuales.configure(text="Cliente no encontrado.")
            self.etiqueta_descuento.configure(text="Descuento (Puntos): $0.00")
            
        self.calcular_totales()
        
    def evento_registrar_venta(self):
        items = []
        for child in self.tabla_ticket.get_children():
            val = self.tabla_ticket.item(child)["values"]
            desc_completa = str(val[0])
            id_prod = desc_completa.split("]")[0].replace("[", "")
            nombre = desc_completa.split("] ")[1] if "] " in desc_completa else "Producto"
            cant = int(val[1])
            prec = float(str(val[2]).replace("$", ""))
            subt = float(str(val[3]).replace("$", ""))
            items.append((id_prod, cant, prec, subt, nombre))
            
        if not items:
            messagebox.showwarning("Ticket Vacío", "No hay productos para cobrar.")
            return
            
        telefono = self.entrada_telefono_venta.get()
        if telefono and db_manager.obtener_puntos_cliente(telefono) is None:
            telefono = None 
            
        total = float(self.etiqueta_total_final.cget("text").split("$")[1])
        subtotal = float(self.etiqueta_subtotal.cget("text").split("$")[1])
        desc_text = self.etiqueta_descuento.cget("text")
        descuento_usado = "10%" in desc_text
        
        if descuento_usado:
            puntos_generados = 0
        else:
            puntos_generados = 10 if subtotal > 500 else 0
            
        id_usuario = 1 # Para simplificar la demostración, usamos el ID 1 por defecto
        
        exito, msg = db_manager.registrar_venta(id_usuario, telefono, total, descuento_usado, puntos_generados, items)
        if exito:
            # === INTEGRACIÓN FACTURA ===
            factura_enviada_msg = ""
            if telefono:
                nombre_cliente, correo_cliente, rfc_cliente = db_manager.obtener_datos_facturacion(telefono)
                if correo_cliente:
                    datos_venta = {
                        "telefono": telefono,
                        "nombre_cliente": nombre_cliente,
                        "rfc": rfc_cliente if rfc_cliente else "Público General",
                        "total": total,
                        "puntos_generados": puntos_generados,
                        "items": items
                    }
                    envio_ok, envio_msg = facturacion.generar_y_enviar_factura(datos_venta, correo_cliente)
                    if envio_ok:
                        factura_enviada_msg = f"\nFactura enviada al correo: {correo_cliente}"
                    else:
                        factura_enviada_msg = f"\nVenta guardada, pero falló el envío de factura: {envio_msg}"
                else:
                    factura_enviada_msg = "\nℹ️ Cliente sin correo electrónico. No se envió factura."
            else:
                factura_enviada_msg = "\nℹVenta a Público General. No se generó factura."
                
            messagebox.showinfo("Venta Exitosa", f"{msg}\nCambio: $0.00\nPuntos generados: {puntos_generados}{factura_enviada_msg}")
            for item in self.tabla_ticket.get_children():
                self.tabla_ticket.delete(item)
            self.entrada_telefono_venta.delete(0, "end")
            self.etiqueta_puntos_actuales.configure(text="PUNTOS: -- \nSin Descuento.")
            self.etiqueta_descuento.configure(text="Descuento (Puntos): $0.00")
            self.calcular_totales()
        else:
            messagebox.showerror("Error", msg)

# --- Ejecución Independiente ---
if __name__ == "__main__":
    raiz = ctk.CTk()
    raiz.title("Farmacia CUCEI - Punto de Venta (Registro)")
    raiz.geometry("1100x700")
    app_ventas = PantallaVentas(raiz)
    app_ventas.pack(fill="both", expand=True)
    raiz.mainloop()
