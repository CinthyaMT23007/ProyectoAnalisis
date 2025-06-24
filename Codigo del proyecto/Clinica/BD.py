import mysql.connector

def conexionBD():
    conexion = mysql.connector.connect(
        host ="localhost",
        user ="root",
        passwd ="",
        database = "clinica"
        )
    if conexion:
        print ("Conexion exitosa a BD")
        return conexion
    else:
        print("Error en la conexion a BD")