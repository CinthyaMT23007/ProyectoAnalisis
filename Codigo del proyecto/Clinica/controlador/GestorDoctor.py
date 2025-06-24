from BD import conexionBD
from flask import flash

def obtener_doctores():
    conexion = conexionBD()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM medico")
    datos = cursor.fetchall()
    conexion.close()
    return datos

def insertar_doctor(nombre, apellido, especialidad, telefono,usuario,contra):
    try:
        con = conexionBD()
        cursor = con.cursor()
        cursor.callproc('sp_registrar_medico',( nombre,
                        apellido,telefono,
                        especialidad,
                        usuario,
                        contra))
        con.commit()
        con.close()
        flash("Medico registrado exitosamente", "success")
    except Exception as e:
        flash(f"Error al registrar medico: {e}", "danger")

def eliminar_doctores(codigo):
    conexion = conexionBD()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM medico WHERE CodMedico = %s", (codigo,))
    conexion.commit()
    conexion.close()

def actualizar_doctor(codigo, nombre, apellido, especialidad, telefono):
    try:
        conexion = conexionBD()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE medico
            SET nombre = %s, apellido = %s, IdEspecialidad = %s, telefono = %s
            WHERE CodMedico = %s
        """, (nombre, apellido, especialidad, telefono, codigo))
        conexion.commit()
        conexion.close()
        flash("Medico actualizado correctamente", "success")
    except Exception as e:
        flash(f"Error al actualizar medico: {e}", "danger")


def obtener_especialidad():
    conexion = conexionBD()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM especialidad")
    roles = cursor.fetchall()
    conexion.close()
    return roles
