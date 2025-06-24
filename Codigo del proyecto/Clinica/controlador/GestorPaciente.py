from BD import *
from flask import flash

def crear_paciente_en_bd(datos):
    try:
        con = conexionBD()
        cursor = con.cursor()
        cursor.callproc('sp_registrar_paciente', datos)
        con.commit()
        con.close()
        flash("Paciente registrado exitosamente", "success")
    except Exception as e:
        flash(f"Error al registrar paciente: {e}", "danger")

def actualizar_paciente_en_bd(datos):
    try:
        con = conexionBD()
        cursor = con.cursor()
        sql = """
        UPDATE paciente SET
        Nombre=%s, Apellido=%s, Edad=%s, DUI=%s,
        Direccion=%s, Telefono=%s
        WHERE CodExpediente=%s
        """
        cursor.execute(sql, datos)
        con.commit()
        con.close()
        flash("Paciente actualizado correctamente", "success")
    except Exception as e:
        flash(f"Error al actualizar paciente: {e}", "danger")

def eliminar_paciente_en_bd(cod):
    try:
        con = conexionBD()
        cursor = con.cursor()
        cursor.execute("DELETE FROM paciente WHERE CodExpediente=%s", (cod,))
        con.commit()
        con.close()
        flash("Paciente eliminado correctamente", "success")
    except Exception as e:
        flash(f"Error al eliminar paciente: {e}", "danger")

def obtener_pacientes():
    try:
        con = conexionBD()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM paciente")
        return cursor.fetchall()
    except Exception as e:
        flash(f"Error al obtener pacientes: {e}", "danger")
        return []
