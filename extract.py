def extract_coordis(cursor):
  query = """  
    SELECT 
      DISTINCT p.prestacion_coordi, 
      CONCAT(p.coordi_apellido, ', ', p.coordi_nombre) AS coordinadora,
      c.coordi_mail,
      c.user_id
    FROM 
      v_prestaciones p
    JOIN v_coordinadores c 
      ON p.prestacion_coordi = c.coordi_id
    WHERE 
      p.prestacion_estado = 1
      AND p.prestacion_coordi IS NOT NULL
      AND p.prestacion_coordi != 14
  """
  cursor.execute(query) 
  return cursor.fetchall()

def extract_pas(cursor, coordi_id):
  
  query = f""" 
    SELECT 
      pa.pa_id,
      CONCAT(pa.pa_apellido, ', ', pa.pa_nombre) AS pa_nombre,
      e.paetiqcat_nombre,
      CASE 
        WHEN pa.pa_estado = 2 THEN 'OK-SIN CASOS'
        WHEN pa.pa_estado = 3 THEN 'EN ADMISIÓN'
      END AS estado_desc,
      pa.pa_obs_saie,
      pa.padispo_nombre,
      pa.pa_ref_busq,
      l.localidad_nombre,
      pa.pa_tel1,
      pa.pa_tel2,
      pa.pa_mail
    FROM 
      v_pas pa
	LEFT JOIN
	  v_etiquetas_pas e
      ON pa.pa_id = e.paetiq_pa
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

def extract_informes(cursor, coord_id):
  query = """ 
    SELECT 
      CONCAT(c.coordi_apellido, ', ', c.coordi_nombre) AS nombre_coordi,
      CONCAT(p.alumno_apellido, ', ', p.alumno_nombre) AS nombre_alumno,
      p.alumno_dni,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Informe Inicial - ADMISIÓN" THEN i.alumnoinforme_id END) AS inf_admision,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Conformidad de PA" THEN i.alumnoinforme_id END) AS conf_pa,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Informe social de seguimiento" THEN i.alumnoinforme_id END) AS inf_social,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Informe Mensual" THEN i.alumnoinforme_id END) AS inf_mensual,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Informe Diagnóstico" THEN i.alumnoinforme_id END) AS inf_diagnostico,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Informe Medio" THEN i.alumnoinforme_id END) AS inf_medio,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "PAC" THEN i.alumnoinforme_id END) AS pac,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "OTRO" THEN i.alumnoinforme_id END) AS otro,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "AA" THEN i.alumnoinforme_id END) AS aa,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "PPI / PI" THEN i.alumnoinforme_id END) AS ppi,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Informe Final" THEN i.alumnoinforme_id END) AS inf_final,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Conformidad familia" THEN i.alumnoinforme_id END) AS conf_familia,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Informe escolar" THEN i.alumnoinforme_id END) AS inf_escolar,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Informe terapéutico ext." THEN i.alumnoinforme_id END) AS inf_ter_ext,
      COUNT(DISTINCT CASE WHEN i.informecat_nombre = "Plan de trabajo - Coordinacion" THEN i.alumnoinforme_id END) AS plan_coordi
    FROM v_prestaciones p
    JOIN v_coordinadores c
        ON p.prestacion_coordi = c.coordi_id
    LEFT JOIN v_informes i 
        ON p.alumno_id = i.alumno_id 
        AND (
            i.alumnoinforme_anio = '2026'
            OR i.informecat_nombre = "Informe Inicial - ADMISIÓN"
        )
    WHERE
        p.prestipo_nombre_corto != 'TERAPIAS'
        AND p.prestacion_estado IN (0, 1)
        AND p.prestacion_anio IN (2026, 2027)
        AND p.prestacion_coordi = %s
    GROUP BY p.alumno_id, p.alumno_dni
    ORDER BY nombre_coordi;
    """
  cursor.execute(query, (coord_id, ))
  return cursor.fetchall()

def extract_seguim(cursor, coord_id):
  query = """ 
    SELECT 
      usuario_carga_nombre,
      s.segalum_rol_carga,
      s.segalum_prestacion,
      p.prestipo_nombre_corto,
      CONCAT(a.alumno_apellido, ', ', a.alumno_nombre) AS nombre_alumno,
      s.segalum_mesanio,
      DATE_FORMAT(s.segalum_fec_carga, '%d-%m-%Y') AS fec_carga,
      s.segcat_nombre
    FROM
      v_seguimientos s
    LEFT JOIN v_prestaciones p
      ON s.segalum_prestacion = p.prestacion_id
    LEFT JOIN v_alumnos a
      ON s.segalum_alumno = a.alumno_id
    WHERE
      (p.prestacion_estado IN (0, 1) OR p.prestacion_estado IS NULL)
      AND YEAR(s.segalum_fec_carga) = 2026 
      AND (p.prestacion_anio IN (2026, 2027) OR p.prestacion_anio IS NULL)
      AND p.prestacion_coordi = %s
    ORDER BY usuario_carga_nombre
  """
  cursor.execute(query, (coord_id, ))
  return cursor.fetchall()

def extract_seguim_mes(cursor, coord_user_id):
  query = """ 
    SELECT
	    CONCAT(a.alumno_apellido, ', ', a.alumno_nombre) AS nombre_alumno,
      p.prestacion_id,
      p.prestipo_nombre_corto,
      s.usuario_carga_nombre,
      s.segalum_rol_carga,     
      SUM(CASE WHEN MONTH(s.segalum_fec_carga) = 1 THEN 1 ELSE 0 END) AS ene,
      SUM(CASE WHEN MONTH(s.segalum_fec_carga) = 2 THEN 1 ELSE 0 END) AS feb,
      SUM(CASE WHEN MONTH(s.segalum_fec_carga) = 3 THEN 1 ELSE 0 END) AS mar,
      SUM(CASE WHEN MONTH(s.segalum_fec_carga) = 4 THEN 1 ELSE 0 END) AS abr,
      SUM(CASE WHEN MONTH(s.segalum_fec_carga) = 5 THEN 1 ELSE 0 END) AS may,
      SUM(CASE WHEN MONTH(s.segalum_fec_carga) = 6 THEN 1 ELSE 0 END) AS jun,
      SUM(CASE WHEN MONTH(s.segalum_fec_carga) = 7 THEN 1 ELSE 0 END) AS jul,
      SUM(CASE WHEN MONTH(s.segalum_fec_carga) = 8 THEN 1 ELSE 0 END) AS ago,
      SUM(CASE WHEN MONTH(s.segalum_fec_carga) = 9 THEN 1 ELSE 0 END) AS sep,
      SUM(CASE WHEN MONTH(s.segalum_fec_carga) = 10 THEN 1 ELSE 0 END) AS oct,
      SUM(CASE WHEN MONTH(s.segalum_fec_carga) = 11 THEN 1 ELSE 0 END) AS nov,
      SUM(CASE WHEN MONTH(s.segalum_fec_carga) = 12 THEN 1 ELSE 0 END) AS dic,
      COUNT(DISTINCT s.segalum_id) AS total_anual
    FROM
      v_seguimientos s
    LEFT JOIN v_prestaciones p
      ON s.segalum_prestacion = p.prestacion_id
    JOIN v_alumnos a
      ON s.segalum_alumno = a.alumno_id
    WHERE
      (p.prestacion_estado IN (0, 1) OR p.prestacion_estado IS NULL)
      AND s.segalum_rol_carga IN ('COORDI', 'EQUIPO_TECNICO')
      AND (p.prestacion_anio IN (2026, 2027) OR p.prestacion_anio IS NULL)
      AND YEAR(s.segalum_fec_carga) = 2026
      AND s.usuario_carga_id = %s
    GROUP BY
      p.prestacion_id,
      a.alumno_id,
      s.usuario_carga_id,
      s.segalum_rol_carga
    ORDER BY
      nombre_alumno;
    """
  cursor.execute(query, (coord_user_id, ))
  return cursor.fetchall()
