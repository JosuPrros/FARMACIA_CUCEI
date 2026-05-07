import smtplib
from email.message import EmailMessage
from datetime import datetime
import os

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
except ImportError:
    print("[ADVERTENCIA] La librería reportlab no está instalada. Para enviar facturas PDF instala con: pip install reportlab")

# --- CREDENCIALES ---
EMAIL_REMITENTE = "farmaciacucei@gmail.com"
PASSWORD_APP = "jndv mivb pcpu vwjw"

def generar_pdf_factura(datos_venta, ruta_pdf):
    """
    Genera un archivo PDF con el ticket/factura usando ReportLab.
    datos_venta debe contener: rfc, total, puntos_generados, items (id_prod, cant, prec, subt)
    """
    try:
        c = canvas.Canvas(ruta_pdf, pagesize=letter)
        ancho, alto = letter
        
        # --- ENCABEZADO ---
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.HexColor("#003B73"))
        c.drawString(50, alto - 50, "FARMACIA CUCEI")
        
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawString(50, alto - 80, "Recibo Electrónico de Compra")
        c.drawString(50, alto - 100, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(50, alto - 120, f"Cliente: {datos_venta.get('nombre_cliente', 'Público General')}")
        rfc_cliente = datos_venta.get('rfc', '')
        if rfc_cliente and rfc_cliente != "Público General":
            c.drawString(50, alto - 140, f"RFC: {rfc_cliente}")
        
        # --- LÍNEA DIVISORIA ---
        c.setStrokeColor(colors.HexColor("#00A4E4"))
        c.setLineWidth(2)
        c.line(50, alto - 160, ancho - 50, alto - 160)
        
        # --- TABLA DE PRODUCTOS ---
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, alto - 190, "CANT")
        c.drawString(100, alto - 190, "DESCRIPCIÓN")
        c.drawString(350, alto - 190, "P. UNIT")
        c.drawString(450, alto - 190, "SUBTOTAL")
        
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(1)
        c.line(50, alto - 200, ancho - 50, alto - 200)
        
        c.setFont("Helvetica", 12)
        y = alto - 220
        for item in datos_venta.get('items', []):
            if len(item) >= 5:
                id_prod, cant, precio, subtot, nombre = item[0], item[1], item[2], item[3], item[4]
            else:
                id_prod, cant, precio, subtot = item[0], item[1], item[2], item[3]
                nombre = f"Producto ID: {id_prod}"
                
            c.drawString(50, y, str(cant))
            c.drawString(100, y, str(nombre)[:35]) # Truncar a 35 caracteres para que no desborde
            c.drawString(350, y, f"${float(precio):.2f}")
            c.drawString(450, y, f"${float(subtot):.2f}")
            y -= 25
            if y < 100:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = alto - 50
        
        # --- TOTALES ---
        y -= 20
        c.setStrokeColor(colors.HexColor("#00A4E4"))
        c.setLineWidth(2)
        c.line(50, y, ancho - 50, y)
        y -= 30
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(300, y, "TOTAL:")
        c.setFillColor(colors.HexColor("#28A745"))
        c.drawString(450, y, f"${datos_venta.get('total', 0.0):.2f}")
        
        # --- PUNTOS ---
        y -= 30
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawString(50, y, f"Puntos ganados en esta compra: {datos_venta.get('puntos_generados', 0)}")
        
        # --- PIE DE PÁGINA ---
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.gray)
        c.drawString(50, 50, "Gracias por tu compra en Farmacia CUCEI. Tu salud es nuestra prioridad.")
        
        c.save()
        return True
    except Exception as e:
        print(f"[ERROR] Al generar PDF: {e}")
        return False

def generar_y_enviar_factura(datos_venta, correo_cliente):
    """
    Coordina la generación del PDF y el envío por correo.
    """
    if not correo_cliente:
        print("[INFO] No hay correo registrado. Factura omitida.")
        return False, "Sin correo"
        
    try:
        import reportlab
    except ImportError:
        return False, "Falta la librería reportlab (pip install reportlab)"
        
    # 1. Generar PDF Temporal
    fecha_str = datetime.now().strftime('%Y%m%d%H%M%S')
    ruta_pdf = f"Factura_{fecha_str}.pdf"
    
    exito_pdf = generar_pdf_factura(datos_venta, ruta_pdf)
    if not exito_pdf:
        return False, "Error al generar el documento PDF"
        
    # 2. Enviar por Correo
    msg = EmailMessage()
    msg['Subject'] = "Tu Recibo de Compra - Farmacia CUCEI"
    msg['From'] = EMAIL_REMITENTE
    msg['To'] = correo_cliente
    
    cuerpo = f"""
    Hola,
    
    Agradecemos tu preferencia. Adjunto a este correo encontrarás el recibo 
    de tu compra en Farmacia CUCEI por un total de ${datos_venta.get('total', 0.0):.2f}.
    
    Puntos ganados: {datos_venta.get('puntos_generados', 0)}
    
    ¡Gracias por cuidarte con nosotros!
    Saludos,
    Equipo Farmacia CUCEI.
    """
    msg.set_content(cuerpo)
    
    # Adjuntar PDF
    try:
        with open(ruta_pdf, 'rb') as f:
            pdf_data = f.read()
        msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=f"Factura_CUCEI_{fecha_str}.pdf")
        
        # Conexión SMTP a Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_REMITENTE, PASSWORD_APP)
            smtp.send_message(msg)
            
        print(f"[INFO] Factura enviada exitosamente a {correo_cliente}")
        
    except Exception as e:
        print(f"[ERROR] Fallo al enviar el correo: {e}")
        return False, f"Fallo al enviar correo: {e}"
    finally:
        # 3. Limpiar PDF temporal
        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)
            
    return True, "Factura generada y enviada correctamente"

# --- MENÚ DE PRUEBAS ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print(" MENÚ DE PRUEBAS: SISTEMA DE FACTURACIÓN ".center(50))
    print("="*50)
    
    while True:
        print("\nOpciones:")
        print("1. Enviar factura de prueba")
        print("2. Salir")
        
        opcion = input("Elige una opción: ").strip()
        
        if opcion == "1":
            correo_destino = input("\nIntroduce el correo destino para la prueba: ").strip()
            if not correo_destino:
                print("-> Error: El correo no puede estar vacío.")
                continue
                
            print("\nGenerando datos de prueba...")
            datos_prueba = {
                "telefono": "3312345678",
                "nombre_cliente": "Juan Pérez",
                "rfc": "PEAJ900101XYZ",
                "total": 540.50,
                "puntos_generados": 54,
                "items": [
                    (1, 2, 100.00, 200.00, "Aspirina 500mg"),   # ID, Cant, Precio, Subtotal, Nombre
                    (5, 1, 340.50, 340.50, "Termómetro Digital")
                ]
            }
            
            print(f"Enviando correo a {correo_destino}...")
            exito, mensaje = generar_y_enviar_factura(datos_prueba, correo_destino)
            
            if exito:
                print(f"-> ¡ÉXITO! {mensaje}")
            else:
                print(f"-> ¡FALLÓ! {mensaje}")
                
        elif opcion == "2":
            print("Saliendo del menú de pruebas...")
            break
        else:
            print("-> Opción no válida.")
