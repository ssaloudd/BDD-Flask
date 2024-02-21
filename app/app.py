from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL

from faker import Faker #
import random #
import time #

app=Flask(__name__)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'escolastico1'
app.config['MYSQL_PORT'] = 3306

conexion = MySQL(app)
fake = Faker() #

# ---------- INICIO ----------
@app.route('/')
def index():
    data = {
        'titulo': 'Index',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    return render_template('index.html', data=data)

# ---------- ALUMNOS ----------
'''
# Ruta para agregar datos falsos (temporal, eliminar después de usar)
@app.route('/agregar-datos-falsos')
def agregar_datos_falsos():
    cursor = conexion.connection.cursor()

    # Generar e insertar 1000 registros en la tabla alumno
    for i in range(1000):
        codigo_alu = f'L0041{i+1}'  # Puedes ajustar la generación de códigos
        cedula_alu = fake.unique.random_number(digits=10)
        apellido_alu = fake.last_name()
        nombre_alu = fake.first_name()
        direccion_alu = fake.address()
        telefono_alu_int = fake.random_int(min=1000000000, max=9999999999)
        telefono_alu = str(telefono_alu_int)[:12]
        email_alu = fake.email()
        genero_alu = random.choice(['Heterosexual', 'Homosexual'])
        fecha_nac_alu = fake.date_of_birth(minimum_age=18, maximum_age=25)
        observaciones_alu = ''

        sql = "INSERT INTO alumno (codigo_alu, cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (codigo_alu, cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu)

        cursor.execute(sql, values)

    # Confirma y cierra la conexión
    conexion.connection.commit()
    cursor.close()

    return redirect(url_for('alumnos'))
'''

@app.route('/alumnos')
def alumnos():
    data = {
        'titulo': 'Alumnos',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    
    return render_template('alumnos.html', data=data)


# -- ALUMNOS: Agregar
@app.route('/agregar-alumno', methods=['POST'])
def agregar_alumno():
    codigo_alu = request.form['codigo_alu']
    cedula_alu = request.form['cedula_alu']
    apellido_alu = request.form['apellido_alu']
    nombre_alu = request.form['nombre_alu']
    direccion_alu = request.form['direccion_alu']
    telefono_alu = request.form['telefono_alu']
    email_alu = request.form['email_alu']
    genero_alu = request.form['genero_alu']
    fecha_nac_alu = request.form['fecha_nac_alu']
    observaciones_alu = request.form['observaciones_alu']

    if codigo_alu and cedula_alu and apellido_alu and nombre_alu and direccion_alu and telefono_alu and email_alu and genero_alu and fecha_nac_alu:
        cursor = conexion.connection.cursor()
        sql = "INSERT INTO alumno (codigo_alu, cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        lista = (codigo_alu, cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu)
        cursor.execute(sql, lista)
        conexion.connection.commit()
        cursor.close()
    return redirect(url_for('alumnos'))

# -- ALUMNOS: Buscar
@app.route('/buscar-alumnos', methods=['POST'])
def buscar_alumnos():
    busqueda = request.form['busqueda']
    cursor = conexion.connection.cursor()
    cursor.execute("SELECT * FROM alumno WHERE codigo_alu LIKE %s", ('%'+busqueda+'%',))
    alumnos = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in alumnos:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    data = {
        'titulo': 'Alumnos',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    return render_template('alumnos.html', data=data, lista=insertObject, busqueda=busqueda)


@app.route('/desplegar-x-alumnos', methods=['POST'])
def desplegar_x_alumnos():
    start_time = time.time() # Captura el tiempo de inicio

    cantidad = int(request.form['cantidad'])
    data = {
        'titulo': 'Alumnos',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    cursor = conexion.connection.cursor()
    cursor.execute(f"SELECT * FROM alumno LIMIT {cantidad}")
    alumnos = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in alumnos:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    elapsed_time = time.time() - start_time # Calcula el tiempo transcurrido
    elapsed_time_sec = int(elapsed_time) # Extrae los segundos enteros
    elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000) # Extrae los milisegundos
    return render_template('alumnos.html', data=data, lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)


@app.route('/mostrar-todos-alumnos', methods=['POST'])
def mostrar_todos_alumnos():
    start_time = time.time() # Captura el tiempo de inicio

    data = {
        'titulo': 'Alumnos',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    cursor = conexion.connection.cursor()
    cursor.execute("SELECT * FROM alumno")
    alumnos = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in alumnos:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    elapsed_time = time.time() - start_time # Calcula el tiempo transcurrido
    elapsed_time_sec = int(elapsed_time) # Extrae los segundos enteros
    elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000) # Extrae los milisegundos
    return render_template('alumnos.html', data=data, lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)


# -- ALUMNOS: Eliminar
@app.route('/eliminar-alumno/<string:codigo_alu>')
def eliminar_alumno(codigo_alu):
    cursor = conexion.connection.cursor()
    sql = "DELETE FROM alumno WHERE codigo_alu=%s"
    data = (codigo_alu,)
    cursor.execute(sql, data)
    conexion.connection.commit()
    cursor.close()
    return redirect(url_for('alumnos'))

# -- ALUMNOS: Editar
@app.route('/editar-alumno/<string:codigo_alu>', methods=['POST'])
def editar_alumno(codigo_alu):
    cedula_alu = request.form['cedula_alu']
    apellido_alu = request.form['apellido_alu']
    nombre_alu = request.form['nombre_alu']
    direccion_alu = request.form['direccion_alu']
    telefono_alu = request.form['telefono_alu']
    email_alu = request.form['email_alu']
    genero_alu = request.form['genero_alu']
    fecha_nac_alu = request.form['fecha_nac_alu']
    observaciones_alu = request.form['observaciones_alu']

    if codigo_alu and cedula_alu and apellido_alu and nombre_alu and direccion_alu and telefono_alu and email_alu and genero_alu and fecha_nac_alu:
        cursor = conexion.connection.cursor()
        sql = "UPDATE alumno SET cedula_alu = %s, apellido_alu = %s, nombre_alu = %s, direccion_alu = %s, telefono_alu = %s, email_alu = %s, genero_alu = %s, fecha_nac_alu = %s, observaciones_alu = %s WHERE codigo_alu = %s"
        lista = (cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu, codigo_alu)
        cursor.execute(sql, lista)
        conexion.connection.commit()
        cursor.close()
    return redirect(url_for('alumnos'))



# ---------- PROFESORES ----------
'''
# Ruta para agregar datos falsos de profesores (temporal, eliminar después de usar)
@app.route('/agregar-datos-falsos-profesores')
def agregar_datos_falsos_profesores():
    cursor = conexion.connection.cursor()

    # Genera e inserta 1000 registros en la tabla profesor
    for i in range(1000):
        codigo_pro = f'P006{i+1}'  # Puedes ajustar la generación de códigos
        cedula_pro = fake.unique.random_number(digits=10)
        apellido_pro = fake.last_name()
        nombre_pro = fake.first_name()
        titulo_pro = fake.job()[:50]
        direccion_pro = fake.address()
        telefono_pro_int = fake.random_int(min=1000000000, max=9999999999)
        telefono_pro = str(telefono_pro_int)[:12]
        email_pro = fake.email()
        genero_pro = 'Heterosexual'
        fecha_nac_pro = fake.date_of_birth(minimum_age=25, maximum_age=60)
        observaciones_pro = ''

        sql = ("INSERT INTO profesor (codigo_pro, cedula_pro, apellido_pro, nombre_pro, "
               "titulo_pro, direccion_pro, telefono_pro, email_pro, genero_pro, fecha_nac_pro, observaciones_pro) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        values = (codigo_pro, cedula_pro, apellido_pro, nombre_pro, titulo_pro, 
                  direccion_pro, telefono_pro, email_pro, genero_pro, fecha_nac_pro, observaciones_pro)

        cursor.execute(sql, values)

    # Confirma y cierra la conexión
    conexion.connection.commit()
    cursor.close()

    return redirect(url_for('profesores'))
'''

@app.route('/profesores')
def profesores():
    data = {
        'titulo': 'Profesores',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    
    return render_template('profesores.html', data=data)

# -- PROFESORES: Agregar
@app.route('/agregar-profesor', methods=['POST'])
def agregar_profesor():
    # Obtener datos del formulario
    codigo_pro = request.form['codigo_pro']
    cedula_pro = request.form['cedula_pro']
    apellido_pro = request.form['apellido_pro']
    nombre_pro = request.form['nombre_pro']
    titulo_pro = request.form['titulo_pro']
    direccion_pro = request.form['direccion_pro']
    telefono_pro = request.form['telefono_pro']
    email_pro = request.form['email_pro']
    genero_pro = request.form['genero_pro']
    fecha_nac_pro = request.form['fecha_nac_pro']
    observaciones_pro = request.form['observaciones_pro']

    cursor = conexion.connection.cursor()
    sql = ("INSERT INTO profesor (codigo_pro, cedula_pro, apellido_pro, nombre_pro, "
           "titulo_pro, direccion_pro, telefono_pro, email_pro, genero_pro, fecha_nac_pro, observaciones_pro) "
           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    cursor.execute(sql, (codigo_pro, cedula_pro, apellido_pro, nombre_pro, titulo_pro, 
                         direccion_pro, telefono_pro, email_pro, genero_pro, fecha_nac_pro, observaciones_pro))
    conexion.connection.commit()
    cursor.close()
    return redirect(url_for('profesores'))

# -- PROFESORES: Buscar
@app.route('/buscar-profesores', methods=['POST'])
def buscar_profesores():
    busqueda = request.form['busqueda']
    cursor = conexion.connection.cursor()
    cursor.execute("SELECT * FROM profesor WHERE codigo_pro LIKE %s", ('%'+busqueda+'%',))
    profesores = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in profesores:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    data = {
        'titulo': 'Profesores',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    return render_template('profesores.html', data=data, lista=insertObject, busqueda=busqueda)

@app.route('/desplegar-x-profesores', methods=['POST'])
def desplegar_x_profesores():
    start_time = time.time() # Captura el tiempo de inicio

    cantidad = int(request.form['cantidad'])
    data = {
        'titulo': 'Profesores',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    cursor = conexion.connection.cursor()
    cursor.execute(f"SELECT * FROM profesor LIMIT {cantidad}")
    profesores = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in profesores:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    elapsed_time = time.time() - start_time # Calcula el tiempo transcurrido
    elapsed_time_sec = int(elapsed_time) # Extrae los segundos enteros
    elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000) # Extrae los milisegundos
    return render_template('profesores.html', data=data, lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)


@app.route('/mostrar-todos-profesores', methods=['POST'])
def mostrar_todos_profesores():
    start_time = time.time() # Captura el tiempo de inicio

    data = {
        'titulo': 'Profesores',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    cursor = conexion.connection.cursor()
    cursor.execute("SELECT * FROM profesor")
    profesores = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in profesores:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    elapsed_time = time.time() - start_time # Calcula el tiempo transcurrido
    elapsed_time_sec = int(elapsed_time) # Extrae los segundos enteros
    elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000) # Extrae los milisegundos
    return render_template('profesores.html', data=data, lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)

# -- PROFESORES: Eliminar
@app.route('/eliminar-profesor/<string:codigo_pro>')
def eliminar_profesor(codigo_pro):
    cursor = conexion.connection.cursor()
    cursor.execute("DELETE FROM profesor WHERE codigo_pro = %s", [codigo_pro])
    conexion.connection.commit()
    cursor.close()
    return redirect(url_for('profesores'))

# -- PROFESORES: Editar
@app.route('/editar-profesor/<string:codigo_pro>', methods=['POST'])
def editar_profesor(codigo_pro):
    cedula_pro = request.form['cedula_pro']
    apellido_pro = request.form['apellido_pro']
    nombre_pro = request.form['nombre_pro']
    titulo_pro = request.form['titulo_pro']
    direccion_pro = request.form['direccion_pro']
    telefono_pro = request.form['telefono_pro']
    email_pro = request.form['email_pro']
    genero_pro = request.form['genero_pro']
    fecha_nac_pro = request.form['fecha_nac_pro']
    observaciones_pro = request.form['observaciones_pro']

    cursor = conexion.connection.cursor()
    sql = ("UPDATE profesor SET cedula_pro = %s, apellido_pro = %s, nombre_pro = %s, "
           "titulo_pro = %s, direccion_pro = %s, telefono_pro = %s, email_pro = %s, "
           "genero_pro = %s, fecha_nac_pro = %s, observaciones_pro = %s WHERE codigo_pro = %s")
    cursor.execute(sql, (cedula_pro, apellido_pro, nombre_pro, titulo_pro, direccion_pro, 
                         telefono_pro, email_pro, genero_pro, fecha_nac_pro, observaciones_pro, codigo_pro))
    conexion.connection.commit()
    cursor.close()
    return redirect(url_for('profesores'))



# ---------- MATERIAS ----------
'''
# Ruta para agregar datos falsos de materias (temporal, eliminar después de usar)
@app.route('/agregar-datos-falsos-materias')
def agregar_datos_falsos_materias():
    cursor = conexion.connection.cursor()

    # Generar e insertar 100 registros en la tabla materia
    for i in range(100):
        codigo_mat = f'M{i+1}'  # Puedes ajustar la generación de códigos
        nombre_mat = fake.word()
        descripcion_mat = fake.word()
        horas_mat = random.randint(5, 13) * 15  # Ejemplo de generación aleatoria de horas
        creditos_mat = random.randint(1, 3)
        prerequisito_mat = fake.word()
        observaciones_mat = ''

        sql = ("INSERT INTO materia (codigo_mat, nombre_mat, descripcion_mat, horas_mat, creditos_mat, prerequisito_mat, observaciones_mat) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s)")
        values = (codigo_mat, nombre_mat, descripcion_mat, horas_mat, creditos_mat, prerequisito_mat, observaciones_mat)

        cursor.execute(sql, values)

    # Confirma y cierra la conexión
    conexion.connection.commit()
    cursor.close()

    return redirect(url_for('materias'))
'''


@app.route('/materias')
def materias():
    data = {
        'titulo': 'Materias',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    return render_template('materias.html')

# -- MATERIAS: Agregar
@app.route('/agregar-materia', methods=['POST'])
def agregar_materia():
    codigo_mat = request.form['codigo_mat']
    nombre_mat = request.form['nombre_mat']
    descripcion_mat = request.form['descripcion_mat']
    horas_mat = request.form['horas_mat']
    creditos_mat = request.form['creditos_mat']
    prerequisito_mat = request.form['prerequisito_mat']
    observaciones_mat = request.form['observaciones_mat']

    cursor = conexion.connection.cursor()
    sql = ("INSERT INTO materia (codigo_mat, nombre_mat, descripcion_mat, horas_mat, creditos_mat, prerequisito_mat, observaciones_mat) "
           "VALUES (%s, %s, %s, %s, %s, %s, %s)")
    cursor.execute(sql, (codigo_mat, nombre_mat, descripcion_mat, horas_mat, creditos_mat, prerequisito_mat, observaciones_mat))
    conexion.connection.commit()
    cursor.close()
    return redirect(url_for('materias'))

# -- MATERIAS: Buscar
@app.route('/buscar-materias', methods=['POST'])
def buscar_materias():
    busqueda = request.form['busqueda']
    cursor = conexion.connection.cursor()
    cursor.execute("SELECT * FROM materia WHERE codigo_mat LIKE %s", ('%' + busqueda + '%',))
    materias = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in materias:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    data = {
        'titulo': 'Materias',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    return render_template('materias.html', data=data, lista=insertObject, busqueda=busqueda)

@app.route('/desplegar-x-materias', methods=['POST'])
def desplegar_x_materias():
    start_time = time.time() # Captura el tiempo de inicio

    cantidad = int(request.form['cantidad'])
    data = {
        'titulo': 'Materias',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    cursor = conexion.connection.cursor()
    cursor.execute(f"SELECT * FROM materia LIMIT {cantidad}")
    profesores = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in profesores:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    elapsed_time = time.time() - start_time # Calcula el tiempo transcurrido
    elapsed_time_sec = int(elapsed_time) # Extrae los segundos enteros
    elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000) # Extrae los milisegundos
    return render_template('materias.html', data=data, lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)


@app.route('/mostrar-todas-materias', methods=['POST'])
def mostrar_todas_materias():
    start_time = time.time() # Captura el tiempo de inicio

    data = {
        'titulo': 'Materias',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    cursor = conexion.connection.cursor()
    cursor.execute("SELECT * FROM materia")
    profesores = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in profesores:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    elapsed_time = time.time() - start_time # Calcula el tiempo transcurrido
    elapsed_time_sec = int(elapsed_time) # Extrae los segundos enteros
    elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000) # Extrae los milisegundos
    return render_template('materias.html', data=data, lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)

# -- MATERIAS: Eliminar
@app.route('/eliminar-materia/<string:codigo_mat>')
def eliminar_materia(codigo_mat):
    cursor = conexion.connection.cursor()
    cursor.execute("DELETE FROM materia WHERE codigo_mat = %s", [codigo_mat])
    conexion.connection.commit()
    cursor.close()
    return redirect(url_for('materias'))

# -- MATERIAS: Editar
@app.route('/editar-materia/<string:codigo_mat>', methods=['POST'])
def editar_materia(codigo_mat):
    nombre_mat = request.form['nombre_mat']
    descripcion_mat = request.form['descripcion_mat']
    horas_mat = request.form['horas_mat']
    creditos_mat = request.form['creditos_mat']
    prerequisito_mat = request.form['prerequisito_mat']
    observaciones_mat = request.form['observaciones_mat']

    cursor = conexion.connection.cursor()
    sql = ("UPDATE materia SET nombre_mat = %s, descripcion_mat = %s, horas_mat = %s, "
           "creditos_mat = %s, prerequisito_mat = %s, observaciones_mat = %s WHERE codigo_mat = %s")
    cursor.execute(sql, (nombre_mat, descripcion_mat, horas_mat, creditos_mat, prerequisito_mat, observaciones_mat, codigo_mat))
    conexion.connection.commit()
    cursor.close()
    return redirect(url_for('materias'))



# ---------- NOTAS ----------
@app.route('/notas')
def notas():
    cursor = conexion.connection.cursor()
    cursor.execute("SELECT * FROM nota")
    notas = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in notas:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('notas.html', lista=insertObject)

# -- NOTAS: Agregar
@app.route('/agregar-nota', methods=['POST'])
def agregar_nota():
    codigo_not = request.form['codigo_not']
    nota1_not = request.form['nota1_not']
    nota2_not = request.form['nota2_not']
    nota3_not = request.form['nota3_not']
    fecha_not = request.form['fecha_not']
    observaciones_not = request.form['observaciones_not']
    codigo_alu = request.form['codigo_alu']
    codigo_pro = request.form['codigo_pro']
    codigo_mat = request.form['codigo_mat']

    cursor = conexion.connection.cursor()
    sql = ("INSERT INTO nota (codigo_not, nota1_not, nota2_not, nota3_not, fecha_not, observaciones_not, codigo_alu, codigo_pro, codigo_mat) "
           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    cursor.execute(sql, (codigo_not, nota1_not, nota2_not, nota3_not, fecha_not, observaciones_not, codigo_alu, codigo_pro, codigo_mat))
    conexion.connection.commit()
    cursor.close()
    return redirect(url_for('notas'))

# ---------- NOTAS: Buscar ----------
@app.route('/buscar-notas', methods=['POST'])
def buscar_notas():
    busqueda = request.form['busqueda']
    cursor = conexion.connection.cursor()
    cursor.execute("SELECT * FROM nota WHERE codigo_not LIKE %s", ('%' + busqueda + '%',))
    notas = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in notas:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    data = {
        'titulo': 'Notas',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    return render_template('notas.html', data=data, lista=insertObject, busqueda=busqueda)

@app.route('/desplegar-x-notas', methods=['POST'])
def desplegar_x_notas():
    start_time = time.time() # Captura el tiempo de inicio

    cantidad = int(request.form['cantidad'])
    data = {
        'titulo': 'Notas',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    cursor = conexion.connection.cursor()
    cursor.execute(f"SELECT * FROM nota LIMIT {cantidad}")
    profesores = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in profesores:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    elapsed_time = time.time() - start_time # Calcula el tiempo transcurrido
    elapsed_time_sec = int(elapsed_time) # Extrae los segundos enteros
    elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000) # Extrae los milisegundos
    return render_template('notas.html', data=data, lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)


@app.route('/mostrar-todas-notas', methods=['POST'])
def mostrar_todas_notas():
    start_time = time.time() # Captura el tiempo de inicio

    data = {
        'titulo': 'Notas',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    cursor = conexion.connection.cursor()
    cursor.execute("SELECT * FROM nota")
    profesores = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in profesores:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    elapsed_time = time.time() - start_time # Calcula el tiempo transcurrido
    elapsed_time_sec = int(elapsed_time) # Extrae los segundos enteros
    elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000) # Extrae los milisegundos
    return render_template('notas.html', data=data, lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)


# -- NOTAS: Eliminar
@app.route('/eliminar-nota/<string:codigo_not>')
def eliminar_nota(codigo_not):
    cursor = conexion.connection.cursor()
    cursor.execute("DELETE FROM nota WHERE codigo_not = %s", [codigo_not])
    conexion.connection.commit()
    cursor.close()
    return redirect(url_for('notas'))

# -- NOTAS: Editar
@app.route('/editar-nota/<string:codigo_not>', methods=['POST'])
def editar_nota(codigo_not):
    nota1_not = request.form['nota1_not']
    nota2_not = request.form['nota2_not']
    nota3_not = request.form['nota3_not']
    fecha_not = request.form['fecha_not']
    observaciones_not = request.form['observaciones_not']
    codigo_alu = request.form['codigo_alu']
    codigo_pro = request.form['codigo_pro']
    codigo_mat = request.form['codigo_mat']

    cursor = conexion.connection.cursor()
    sql = ("UPDATE nota SET nota1_not = %s, nota2_not = %s, nota3_not = %s, fecha_not = %s, "
           "observaciones_not = %s, codigo_alu = %s, codigo_pro = %s, codigo_mat = %s WHERE codigo_not = %s")
    cursor.execute(sql, (nota1_not, nota2_not, nota3_not, fecha_not, observaciones_not, codigo_alu, codigo_pro, codigo_mat, codigo_not))
    conexion.connection.commit()
    cursor.close()
    return redirect(url_for('notas'))


if __name__=='__main__':
    app.run(debug=True, port=5000)