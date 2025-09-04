import mysql.connector
from dotenv import load_dotenv
import os

# --- CARGAR VARIABLES DE ENTORNO ---
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

def connect_db():
  try:
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    print("Conexión a la base de datos exitosa.")
    return conn
  except Exception as e:
    print("Error al conectar a la base de datos:", e)
    exit(1)