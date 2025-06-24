from BD import conexionBD

def obtener_citas():
    con = conexionBD()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM cita")
    citas = cursor.fetchall()
    con.close()
    return citas

def crear_cita(paciente_id, doctor, fecha, hora, motivo):
    con = conexionBD()
    cursor = con.cursor()
    cursor.execute("INSERT INTO cita (paciente_id, doctor, fecha, hora, motivo) VALUES (%s, %s, %s, %s, %s)",
                   (paciente_id, doctor, fecha, hora, motivo))
    con.commit()
    con.close()

def eliminar_cita(id):
    con = conexionBD()
    cursor = con.cursor()
    cursor.execute("DELETE FROM cita WHERE id = %s", (id,))
    con.commit()
    con.close()

def editar_cita(id, paciente_id, doctor, fecha, hora, motivo):
    con = conexionBD()
    cursor = con.cursor()
    cursor.execute("UPDATE cita SET paciente_id=%s, doctor=%s, fecha=%s, hora=%s, motivo=%s WHERE id=%s",
                   (paciente_id, doctor, fecha, hora, motivo, id))
    con.commit()
    con.close()


