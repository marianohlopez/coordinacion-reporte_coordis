from openpyxl import Workbook
from openpyxl.styles import Font
from dotenv import load_dotenv
import os
import yagmail
from extract import extract_coordis, extract_pas

load_dotenv()

MAIL_AUTOR = os.getenv("MAIL_AUTOR")
APP_GMAIL_PASS = os.getenv("APP_GMAIL_PASS")
MAIL_DESTINO = os.getenv("MAIL_DESTINO")

def enviar_mail(destinatario, subject, body, archivo_adjunto):
  try:
    yag = yagmail.SMTP(MAIL_AUTOR, APP_GMAIL_PASS)
    yag.send(
        to=destinatario,
        subject=subject,
        contents=body,
        attachments=archivo_adjunto
    )
    print(f"📧 Mail enviado a {destinatario}")
  except Exception as e:
    print(f"❌ Error enviando mail a {destinatario}: {e}")


def generar_excel_por_coordinadora(coord_nombre, pas, coord_mail):
    wb = Workbook()
    ws = wb.active
    ws.title = "PAs disponibles"

    headers = ["PA ID", "NOMBRE", "LOCALIDAD", "TELEFONO", "TELEFONO 2","EMAIL"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for pa in pas:
        ws.append(pa)

    filename = f"reporte_{coord_nombre.replace(', ', '_')}.xlsx"
    wb.save(filename)
    print(f"✅ Excel generado: {filename}")

    # enviar_mail(
    #     destinatario=coord_mail,
    #     subject=f"Reporte de PAs disponibles - {coord_nombre} (NO CONTESTAR)",
    #     body=f"""Hola {coord_nombre},\n\nAdjunto encontrarás el listado actualizado de PAs 
    #       disponibles en tus localidades.\n\nSaludos,\nMariano López.""",
    #     archivo_adjunto=filename
    # )

def generar_reportes_por_coordinadora(conn):
    cursor = conn.cursor()

    coordinadoras = extract_coordis(cursor)

    for coord in coordinadoras:
      coord_id = coord[0]
      coord_nombre = coord[1]
      coord_mail = coord[2]

      pas = extract_pas(cursor, coord_id)
      generar_excel_por_coordinadora(coord_nombre, pas, coord_mail)

