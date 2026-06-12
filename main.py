from db import connect_db, register_report
from transform import generar_reportes_por_coordinadora

def main(): 
  conn = connect_db()
  cant, registros = generar_reportes_por_coordinadora(conn)
  register_report(cant, registros)
  conn.close()

if __name__ == "__main__":
  main()
