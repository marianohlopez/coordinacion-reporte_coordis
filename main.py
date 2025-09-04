from db import connect_db
from transform import generar_reportes_por_coordinadora

def main(): 
  conn = connect_db()
  generar_reportes_por_coordinadora(conn)
  conn.close()

if __name__ == "__main__":
  main()
