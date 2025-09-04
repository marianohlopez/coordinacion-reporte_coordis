def extract_coordis(cursor):
  query = """  
    SELECT 
    DISTINCT p.prestacion_coordi, 
      CONCAT(p.coordi_apellido, ', ', p.coordi_nombre) AS coordinadora,
      c.coordi_mail
    FROM 
      v_prestaciones p
    JOIN v_coordinadores c 
      ON p.prestacion_coordi = c.coordi_id
    WHERE 
      p.prestacion_estado = 1
          AND p.prestacion_coordi IS NOT NULL
          AND p.prestacion_estado_descrip != "TERAPIAS"
  """
  cursor.execute(query) 
  return cursor.fetchall()

def extract_pas(cursor, coordi_id):
  
  query = f""" 
    SELECT 
      pa.pa_id,
      CONCAT(pa.pa_apellido, ', ', pa.pa_nombre) AS pa_nombre,
      l.localidad_nombre,
      pa.pa_tel1,
      pa.pa_tel2,
      pa.pa_mail
    FROM 
      v_pas pa
    JOIN 
      v_localidades l 
      ON pa.pa_localidad = l.localidad_id
    WHERE pa.pa_estado IN (2,3) 
      AND pa.pa_localidad IN (
            SELECT DISTINCT e.escuela_localidad
            FROM v_prestaciones p
            JOIN v_escuelas e ON p.prestacion_escuela = e.escuela_id
            WHERE p.prestacion_coordi = {coordi_id}
      )
    ORDER BY l.localidad_nombre, pa_nombre;
  """
  cursor.execute(query)
  return cursor.fetchall()

