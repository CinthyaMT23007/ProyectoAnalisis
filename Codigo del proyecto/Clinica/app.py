from flask import Flask, render_template, request, redirect, url_for, jsonify,session
from datetime import datetime, timedelta,date 
import json
from controlador.GestorPaciente import *
from controlador.GestorCitas import *
from controlador.GestorDoctor import *

app = Flask(__name__)
app.secret_key = 'clave-secreta'  # Necesaria si usas sesiones o formularios seguros

# Página de inicio
@app.route('/')
def inicio():
    if 'idrol' not in session:
        return redirect(url_for("login"))

    conexion = conexionBD()
    cursor = conexion.cursor()

    idrol = session['idrol']
    context = {}

    if idrol == 1:  # Admin
        cursor.execute("SELECT COUNT(*) FROM paciente")
        context['total_pacientes'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM cita WHERE IdEstado = 1")
        context['total_citas'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM medico")
        context['total_doctores'] = cursor.fetchone()[0]

        cursor.execute("""SELECT p.Nombre,p.apellido, m.Nombre, m.apellido, c.FechaCita, c.HoraCita
                          FROM cita c JOIN paciente p ON c.CodExpediente = p.CodExpediente
                          JOIN medico m ON c.CodMedico = m.CodMedico
                          ORDER BY c.FechaCita LIMIT 5""")
        context['citas_proximas'] = [
            {
                'paciente_nombre': r[0],
                'paciente_apellido': r[1],
                'doctor_nombre': r[2],
                'doctor_apellido': r[3],
                'fecha': r[4].strftime('%d/%m/%Y'),
                'hora': str(r[5])[:5]  # ← solución clave
            }
            for r in cursor.fetchall()
]

    elif idrol == 2:  # Médico
        cod_usuario = session['codUsuario']
        cursor.execute("SELECT CodMedico FROM medico WHERE CodUsuario = %s", (cod_usuario,))
        cod_medico = cursor.fetchone()[0]

        # Citas para hoy
        cursor.execute("""
            SELECT p.Nombre, c.HoraCita, c.Motivo
            FROM cita c 
            JOIN paciente p ON c.CodExpediente = p.CodExpediente
            WHERE c.CodMedico = %s AND c.FechaCita = CURDATE()
            ORDER BY c.HoraCita ASC
        """, (cod_medico,))
        citas_hoy = cursor.fetchall()
        context['citas_hoy'] = [{'nombre_paciente': r[0], 'hora': r[1], 'motivo': r[2]} for r in citas_hoy]
        context['total_citas_hoy'] = len(citas_hoy)

        cursor.execute("""SELECT COUNT(*) FROM cita
                        WHERE CodMedico = %s AND FechaCita > CURDATE()""", (cod_medico,))
        context['total_citas_programadas'] = cursor.fetchone()[0]


        # Citas futuras (desde mañana en adelante)
        cursor.execute("""
            SELECT p.Nombre, c.FechaCita, c.HoraCita
            FROM cita c 
            JOIN paciente p ON c.CodExpediente = p.CodExpediente
            WHERE c.CodMedico = %s AND c.FechaCita > CURDATE()
            ORDER BY c.FechaCita ASC, c.HoraCita ASC
        """, (cod_medico,))
        citas_futuras = cursor.fetchall()
        context['citas_futuras'] = [{'nombre_paciente': r[0], 'fecha': r[1], 'hora': r[2]} for r in citas_futuras]

    elif idrol == 3:  # Paciente
        cod_usuario = session['codUsuario']
        cursor.execute("SELECT CodExpediente FROM paciente WHERE CodUsuario = %s", (cod_usuario,))
        cod_exp = cursor.fetchone()[0]

        cursor.execute("""SELECT m.Nombre, c.FechaCita, c.HoraCita
                          FROM cita c JOIN medico m ON c.CodMedico = m.CodMedico
                          WHERE c.CodExpediente = %s AND c.FechaCita >= CURDATE()""", (cod_exp,))
        citas = cursor.fetchall()
        context['citas_proximas'] = [{'doctor': r[0], 'fecha': r[1], 'hora': r[2]} for r in citas]

    elif idrol == 4:  # Recepcionista
        cursor.execute("SELECT COUNT(*) FROM cita WHERE IdEstado = 1")
        context['total_pendientes'] = cursor.fetchone()[0]

        cursor.execute("""SELECT p.Nombre, c.FechaCita, c.HoraCita
                          FROM cita c JOIN paciente p ON c.CodExpediente = p.CodExpediente
                          ORDER BY c.FechaCita DESC LIMIT 5""")
        ultimas = cursor.fetchall()
        context['ultimas_citas'] = [{'paciente': r[0], 'fecha': r[1], 'hora': r[2]} for r in ultimas]

    return render_template("inicio.html", **context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contra = request.form['contra']

        conexion = conexionBD()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT codUsuario, usuario, idrol FROM Usuario
            WHERE usuario = %s AND contraseña = %s
        """, (usuario, contra))

        user = cursor.fetchone()

        if user:
            session['codUsuario'] = user[0]
            session['usuario'] = user[1]
            session['idrol'] = user[2]

            flash(f"Bienvenido {user[1]}", "success")

            return redirect(url_for('inicio'))  # Redirige a la página común

        else:
            flash("Usuario o contraseña incorrectos.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for('login'))

@app.route('/pacientes')
def pacientes():
    pacientes = obtener_pacientes()
    return render_template('pacientes.html', pacientes=pacientes)

@app.route('/crear', methods=['POST'])
def crear_paciente():
    datos = (
        request.form['nombre'],
        request.form['apellido'],
        request.form['edad'],
        request.form['dui'],
        request.form['direccion'],
        request.form['telefono'],
        request.form['usuario'],
        request.form['contrase']
    )
    crear_paciente_en_bd(datos)
    return redirect(url_for('pacientes'))

@app.route('/editar', methods=['POST'])
def editar_paciente():
    datos = (
        request.form['nombre'],
        request.form['apellido'],
        request.form['edad'],
        request.form['dui'],
        request.form['direccion'],
        request.form['telefono'],
        request.form['cod']
    )
    actualizar_paciente_en_bd(datos)
    return redirect(url_for('pacientes'))

@app.route('/eliminar/<cod>', methods=['POST'])
def eliminar_paciente(cod):
    eliminar_paciente_en_bd(cod)
    return redirect(url_for('pacientes'))



@app.route("/citas", methods=["GET", "POST"])
def citas():
    conexion = conexionBD()
    cursor = conexion.cursor()

    # Obtener pacientes para datalist
    cursor.execute("SELECT CodExpediente, Nombre, Apellido FROM Paciente ORDER BY Nombre")
    pacientes = cursor.fetchall()

    fecha_form = request.form.get("fecha") if request.method == "POST" else None
    medicos_disponibles = []

    # Diccionario días de semana (lo tienes bien)
    dias_semana = {
        0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
        4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
    }

    # Función para generar bloques (la tienes bien)
    def generar_bloques_horario(inicio, fin, duracion_min=30):
        bloques = []
        hora_actual = inicio
        while hora_actual + timedelta(minutes=duracion_min) <= fin:
            bloques.append(hora_actual.strftime("%H:%M:%S"))
            hora_actual += timedelta(minutes=duracion_min)
        return bloques

    # Si hay fecha seleccionada
    if fecha_form:
        fecha_dt = datetime.strptime(fecha_form, "%Y-%m-%d")
        dia_seleccionado = dias_semana[fecha_dt.weekday()]

        cursor.execute("""
            SELECT m.CodMedico, m.Nombre, m.Apellido, h.HoraInicio, h.HoraFin
            FROM Medico m
            JOIN HorarioMedico h ON m.CodMedico = h.CodMedico
            WHERE h.DiaSemana = %s
        """, (dia_seleccionado,))
        resultados = cursor.fetchall()

        for medico in resultados:
            codmedico, nombre, apellido, hora_inicio, hora_fin = medico

            hi = datetime.strptime(str(hora_inicio), "%H:%M:%S")
            hf = datetime.strptime(str(hora_fin), "%H:%M:%S")

            bloques = generar_bloques_horario(hi, hf)

            # Excluir citas canceladas
            cursor.execute("""
                SELECT c.HoraCita
                FROM Cita c
                JOIN estadocita e ON c.IdEstado = e.IdEstado
                WHERE c.CodMedico = %s AND c.FechaCita = %s
                AND e.NombreEstado IN ('Pendiente', 'Reprogramada')
            """, (codmedico, fecha_form))
            citas = cursor.fetchall()

            horas_ocupadas = []
            for c in citas:
                hora_cita = c[0]
                if isinstance(hora_cita, str):
                    hora_cita = datetime.strptime(hora_cita, "%H:%M:%S").time()
                elif isinstance(hora_cita, timedelta):
                    hora_cita = (datetime.min + hora_cita).time()
                horas_ocupadas.append(hora_cita.strftime("%H:%M:%S"))

            bloques_disponibles = [b for b in bloques if b not in horas_ocupadas]

            if bloques_disponibles:
                medicos_disponibles.append({
                    'codmedico': codmedico,
                    'nombre': nombre,
                    'apellido': apellido,
                    'hora_inicio': str(hora_inicio),
                    'hora_fin': str(hora_fin),
                    'bloques': bloques_disponibles
                })

    # Obtener todas las citas para la tabla
    cursor.execute("""
        SELECT c.CodCita, c.FechaCita, c.HoraCita, c.Motivo,
            p.Nombre, p.Apellido,
            m.Nombre, m.Apellido, m.CodMedico,
            e.NombreEstado
        FROM Cita c
        JOIN Paciente p ON c.CodExpediente = p.CodExpediente
        JOIN Medico m ON c.CodMedico = m.CodMedico
        JOIN estadocita e ON c.IdEstado = e.IdEstado
        ORDER BY c.FechaCita, c.HoraCita
    """)
    citas_originales = cursor.fetchall()

    # Agregar fecha mínima (día siguiente a la cita) para cada cita
    citas = []
    for cita in citas_originales:
        fecha_cita_str = cita[1]  # FechaCita
        fecha_cita_dt = datetime.strptime(str(fecha_cita_str), "%Y-%m-%d")
        min_fecha = (fecha_cita_dt + timedelta(days=1)).strftime("%Y-%m-%d")
        citas.append(cita + (min_fecha,))  # ahora c[10] es min_fecha

    fecha_minima = datetime.now().strftime("%Y-%m-%d")  # fecha mínima para el input principal

    return render_template("citas.html",
                           fecha_form=fecha_form,
                           medicos_disponibles=medicos_disponibles,
                           citas=citas,
                           pacientes=pacientes,
                           fecha_minima=fecha_minima)

@app.route("/guardar_cita", methods=["POST"])
def guardar_cita():
    conexion = conexionBD()
    cursor = conexion.cursor()

    fecha = request.form.get("fecha")
    hora = request.form.get("hora")
    codmedico = request.form.get("codmedico")
    codexpediente = request.form.get("codexpediente")
    motivo = request.form.get("motivo")
    estado=1
    try:
        cursor.execute("""
            INSERT INTO Cita (FechaCita, HoraCita, Motivo, CodExpediente, CodMedico,IdEstado )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (fecha, hora, motivo, codexpediente, codmedico,estado))
        conexion.commit()
        flash("Cita guardada correctamente.", "success")
    except Exception as e:
        conexion.rollback()
        flash(f"Error al guardar la cita: {e}", "danger")

    return redirect(url_for("citas"))

@app.route("/cancelar_cita", methods=["POST"])
def cancelar_cita():
    codcita = request.form.get("codcita")
    conexion = conexionBD()
    cursor = conexion.cursor()

    try:
        cursor.execute("UPDATE Cita SET IdEstado = 3 WHERE CodCita = %s", (codcita,))
        conexion.commit()
        flash("Cita cancelada exitosamente.", "success")
    except Exception as e:
        conexion.rollback()
        flash(f"Error al cancelar la cita: {e}", "danger")

    return redirect(url_for("citas"))

@app.route('/reprogramar_cita_modal', methods=['POST'])
def reprogramar_cita_modal():
    codigo = request.form['codigo']
    codmedico = request.form['codmedico']
    fecha = request.form['nueva_fecha']
    hora = request.form['nueva_hora']

    conexion = conexionBD()
    cursor = conexion.cursor()

    # Función para convertir a objeto time
    def a_time(h):
        if isinstance(h, str):
            return datetime.strptime(h, '%H:%M:%S').time()
        elif isinstance(h, timedelta):
            return (datetime.min + h).time()
        elif hasattr(h, 'time'):  # si ya es datetime.datetime
            return h.time()
        else:
            return h  # asume que ya es time

    # Obtener horario del médico para ese día
    dia_semana = datetime.strptime(fecha, "%Y-%m-%d").strftime('%A')
    dias_es = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    dia_es = dias_es[dia_semana]

    cursor.execute("""
        SELECT HoraInicio, HoraFin FROM HorarioMedico
        WHERE CodMedico = %s AND DiaSemana = %s
    """, (codmedico, dia_es))
    horario = cursor.fetchone()

    if not horario:
        flash('El médico no trabaja ese día.', 'danger')
        return redirect(url_for('citas'))

    hora_inicio, hora_fin = horario
    hora_inicio = a_time(hora_inicio)
    hora_fin = a_time(hora_fin)

    hora_seleccionada = datetime.strptime(hora, '%H:%M').time()

    if not (hora_inicio <= hora_seleccionada <= hora_fin):
        flash('Hora fuera del horario permitido.', 'danger')
        return redirect(url_for('citas'))

    # Actualizar la cita
    cursor.execute("""
        UPDATE Cita SET FechaCita = %s, HoraCita = %s, IdEstado = 2
        WHERE CodCita = %s
    """, (fecha, hora, codigo))
    conexion.commit()

    flash('Cita reprogramada con éxito.', 'success')
    return redirect(url_for('citas'))


@app.route("/horas_disponibles/<codmedico>/<fecha>")
def horas_disponibles(codmedico, fecha):
    print(f"Buscando disponibilidad para médico {codmedico} el {fecha}")
    
    dia_semana = datetime.strptime(fecha, "%Y-%m-%d").strftime('%A')
    dias_es = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes',
        'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    dia_es = dias_es.get(dia_semana)
    print("Día en español:", dia_es)

    conexion = conexionBD()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT HoraInicio, HoraFin FROM HorarioMedico
        WHERE CodMedico = %s AND DiaSemana = %s
    """, (codmedico, dia_es))
    horario = cursor.fetchone()
    print("Horario obtenido:", horario)

    if not horario:
        return jsonify([])

    hora_inicio, hora_fin = horario
    print("Rango:", hora_inicio, "->", hora_fin)

    actual = datetime.strptime(str(hora_inicio), "%H:%M:%S")
    fin = datetime.strptime(str(hora_fin), "%H:%M:%S")
    bloques = []
    while actual < fin:
        bloques.append(actual.strftime('%H:%M'))
        actual += timedelta(minutes=30)
    print("Bloques generados:", bloques)

    cursor.execute("""
        SELECT HoraCita FROM Cita
        WHERE CodMedico = %s AND FechaCita = %s AND IdEstado != 3
    """, (codmedico, fecha))
    horas_ocupadas = [h[0].strftime('%H:%M') for h in cursor.fetchall()]
    print("Horas ocupadas:", horas_ocupadas)

    disponibles = [h for h in bloques if h not in horas_ocupadas]
    print("Disponibles:", disponibles)

    return jsonify(disponibles)

@app.route('/doctores')
def doctores():
    lista = obtener_doctores()
    especialidad=obtener_especialidad()
    return render_template('doctores.html', doctores=lista,especialidad=especialidad)

@app.route('/crear_doctor', methods=['POST'])
def crear_doctor():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    especialidad = request.form['idEspecialidad']
    telefono = request.form['telefono']
    usuario = request.form['usuario']
    contra = request.form['contrase']
    insertar_doctor(nombre, apellido, especialidad, telefono, usuario, contra)
    return redirect(url_for('doctores'))

@app.route('/eliminar_doctor/<codigo>', methods=['POST'])
def eliminar_doctor(codigo):
    eliminar_doctores(codigo)
    return redirect(url_for('doctores'))

@app.route('/editar_doctor', methods=['POST'])
def editar_doctor():
    codigo = request.form['codigo']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    especialidad = request.form['idEspecialidad']
    telefono = request.form['telefono']
    actualizar_doctor(codigo, nombre, apellido, especialidad, telefono)
    return redirect(url_for('doctores'))

@app.route('/mis_citas')
def mis_citas():
    if 'codUsuario' not in session or session.get('idrol') != 2:  # 2 = médico
        flash("Acceso no autorizado.", "danger")
        return redirect(url_for('login'))

    cod_usuario = session['codUsuario']

    conexion = conexionBD()
    cursor = conexion.cursor()

    cursor.execute("SELECT CodMedico FROM Medico WHERE CodUsuario = %s", (cod_usuario,))
    resultado = cursor.fetchone()
    if not resultado:
        flash("No se encontró información del médico.", "danger")
        return redirect(url_for('login'))

    cod_medico = resultado[0]

    cursor.execute("""
        SELECT c.CodCita, c.FechaCita, c.HoraCita, c.Motivo,
               p.Nombre, p.Apellido,
               e.NombreEstado
        FROM Cita c
        JOIN Paciente p ON c.CodExpediente = p.CodExpediente
        JOIN estadocita e ON c.IdEstado = e.IdEstado
        WHERE c.CodMedico = %s
        ORDER BY c.FechaCita, c.HoraCita
    """, (cod_medico,))

    citas = cursor.fetchall()
    hoy = date.today().strftime("%Y-%m-%d")

    return render_template('mis_citas.html', citas=citas, hoy=hoy)

@app.route('/registrar_consulta/<codcita>', methods=['GET', 'POST'])
def registrar_consulta(codcita):
    if 'codUsuario' not in session or session.get('idrol') != 2:
        flash("Acceso no autorizado.", "danger")
        return redirect(url_for('login'))

    conexion = conexionBD()
    cursor = conexion.cursor()

    # Obtener cita
    cursor.execute("""
        SELECT c.FechaCita, c.Motivo, p.CodExpediente, m.CodMedico,
               p.Nombre, p.Apellido
        FROM Cita c
        JOIN Paciente p ON c.CodExpediente = p.CodExpediente
        JOIN Medico m ON c.CodMedico = m.CodMedico
        WHERE c.CodCita = %s
    """, (codcita,))
    cita = cursor.fetchone()

    if not cita:
        flash("Cita no encontrada.", "danger")
        return redirect(url_for('mis_citas'))

    if request.method == 'POST':
        motivo = request.form['motivo']
        diagnostico = request.form['diagnostico']
        fecha = request.form['fecha']
        codexpediente = request.form['codexpediente']
        codmedico = request.form['codmedico']

        # Guardar en historial
        cursor.execute("""
            INSERT INTO historialclinico (CodExpediente, MotivoConsulta, Diagnostico, FechaConsulta, CodMedico)
            VALUES (%s, %s, %s, %s, %s)
        """, (codexpediente, motivo, diagnostico, fecha, codmedico))

        # Marcar cita como completada (IdEstado = 4)
        cursor.execute("UPDATE Cita SET IdEstado = 4 WHERE CodCita = %s", (codcita,))
        conexion.commit()

        flash("Consulta registrada con éxito.", "success")
        return redirect(url_for('mis_citas'))

    # Obtener historial clínico del paciente
    codexpediente = cita[2]
    cursor.execute("""
        SELECT co.FechaConsulta, co.MotivoConsulta, co.Diagnostico,
               m.Nombre, m.Apellido
        FROM historialclinico co
        JOIN Medico m ON co.CodMedico = m.CodMedico
        WHERE co.CodExpediente = %s
        ORDER BY co.FechaConsulta DESC
    """, (codexpediente,))
    historial = cursor.fetchall()

    return render_template('registrar_consulta.html', cita=cita, historial=historial)

@app.route('/historial_clinico', methods=['GET'])
def historial_clinico():
    conexion = conexionBD()
    cursor = conexion.cursor(dictionary=True)  # Para obtener resultados con nombres de columnas

    # Obtener lista de pacientes para el datalist
    cursor.execute("SELECT CodExpediente, Nombre, Apellido FROM Paciente ORDER BY Nombre, Apellido")
    pacientes = cursor.fetchall()

    codexpediente = request.args.get('codexpediente')
    paciente = None
    historial = None

    if codexpediente:
        # Obtener datos del paciente seleccionado
        cursor.execute("SELECT CodExpediente, Nombre, Apellido FROM Paciente WHERE CodExpediente = %s", (codexpediente,))
        paciente = cursor.fetchone()

        # Obtener historial clínico del paciente con datos del médico
        cursor.execute("""
            SELECT h.CodConsulta, h.FechaConsulta, h.MotivoConsulta, h.Diagnostico,
                   m.Nombre AS MedicoNombre, m.Apellido AS MedicoApellido
            FROM historialclinico h
            JOIN Medico m ON h.CodMedico = m.CodMedico
            WHERE h.CodExpediente = %s
            ORDER BY h.FechaConsulta DESC
        """, (codexpediente,))
        historial = cursor.fetchall()

    return render_template('historial_clinico.html', pacientes=pacientes, paciente=paciente, historial=historial)

@app.route("/perfil_paciente")
def perfil_paciente():

    cod_usuario = session['codUsuario']
    conexion = conexionBD()
    cursor = conexion.cursor()

    # Obtener CodExpediente
    cursor.execute("SELECT CodExpediente FROM Paciente WHERE CodUsuario = %s", (cod_usuario,))
    resultado = cursor.fetchone()
    if not resultado:
        flash("Paciente no encontrado", "danger")
        return redirect(url_for("login"))

    codexpediente = resultado[0]
    hoy = datetime.now().strftime("%Y-%m-%d")

    # Citas
    cursor.execute("""
        SELECT c.CodCita, c.FechaCita, c.HoraCita, c.Motivo,
               m.Nombre, m.Apellido, e.NombreEstado
        FROM Cita c
        JOIN Medico m ON c.CodMedico = m.CodMedico
        JOIN estadocita e ON c.IdEstado = e.IdEstado
        WHERE c.CodExpediente = %s
        ORDER BY c.FechaCita DESC, c.HoraCita
    """, (codexpediente,))
    citas = cursor.fetchall()

    # Historial clínico
    cursor.execute("""
        SELECT h.CodConsulta, h.FechaConsulta,
               m.Nombre, m.Apellido,
               h.MotivoConsulta, h.Diagnostico
        FROM historialclinico h
        JOIN Medico m ON h.CodMedico = m.CodMedico
        WHERE h.CodExpediente = %s
        ORDER BY h.FechaConsulta DESC
    """, (codexpediente,))
    historial = cursor.fetchall()

    return render_template("mi_perfil_paciente.html", citas=citas, historial=historial, hoy=hoy)

if __name__ == "__main__":
    app.run(port=3000,debug=True)