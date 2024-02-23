from flask import Flask, render_template, request, url_for, redirect
#from flask_mysqldb import MySQL

from faker import Faker #
import random #
import time #
import pyodbc
fake = Faker()

app=Flask(__name__)

# Configuración de conexión a SQL Server con Windows Authentication
server = 'DESKTOP-PAQ11B3'
database = 'escolastico1'
driver = '{ODBC Driver 17 for SQL Server}'
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

# Función para establecer la conexión a la base de datos
def get_db_connection():
    return pyodbc.connect(conn_str)

# ---------- INICIO ----------
@app.route('/')
def index():
    return render_template('index.html')

# ---------- ALUMNOS ----------
'''
# Ruta para agregar datos falsos (temporal, eliminar después de usar)
@app.route('/agregar-datos-falsos-alumnos')
def agregar_datos_falsos():
    conn = None  # Inicializar la variable conn fuera del bloque try
    try:
        conn = get_db_connection()  # Asegúrate de tener la función get_db_connection() definida

        cursor = conn.cursor()

        # Generar e insertar 1000 registros en la tabla alumno
        for i in range(9):
            codigo_alu = f'L0040220{i+1}'  # Puedes ajustar la generación de códigos
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

            sql = ("INSERT INTO alumno (codigo_alu, cedula_alu, apellido_alu, nombre_alu, "
                   "direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu) "
                   "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
            values = (codigo_alu, cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu)

            cursor.execute(sql, values)

        # Confirma y cierra la conexión
        conn.commit()
        cursor.close()

        return redirect(url_for('alumnos'))
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al agregar datos falsos:", str(e))
        return "Error al agregar datos falsos: " + str(e), 500
    finally:
        if conn:
            conn.close()
'''

@app.route('/alumnos')
def alumnos():
    return render_template('alumnos.html')

# -- ALUMNOS: Agregar
@app.route('/agregar-alumno', methods=['POST'])
def agregar_alumno():
    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Recuperar datos del formulario
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

        # Verificar si los campos obligatorios tienen datos
        if codigo_alu and cedula_alu and apellido_alu and nombre_alu and direccion_alu and telefono_alu and email_alu and genero_alu and fecha_nac_alu:
            # Llamada al stored procedure
            sql = "EXEC sp_agregar_alumno ?, ?, ?, ?, ?, ?, ?, ?, ?, ?"
            params = (codigo_alu, cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu)
            cursor.execute(sql, params)
            conn.commit()

    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al agregar alumno:", str(e))
    finally:
        if conn:
            conn.close()

    return redirect(url_for('alumnos'))

# -- ALUMNOS: Buscar
@app.route('/buscar-alumnos', methods=['POST'])
def buscar_alumnos():
    start_time = time.time()
    busqueda = request.form['busqueda']
    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Llamada al stored procedure
        sql = "EXEC sp_buscar_alumnos ?"
        params = (busqueda,)
        cursor.execute(sql, params)

        # Recuperar resultados
        alumnos = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in alumnos:
            insertObject.append(dict(zip(columnNames, record)))

        cursor.close()

        elapsed_time = time.time() - start_time
        elapsed_time_sec = int(elapsed_time)
        elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000)  # Extrae los milisegundos

        return render_template('alumnos.html', lista=insertObject, busqueda=busqueda, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)

    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al buscar alumnos:", str(e))
        return "Error al buscar el alumno: " + str(e), 500

    finally:
        if conn:
            conn.close()

# -- ALUMNOS: Desplegar x
@app.route('/desplegar-x-alumnos', methods=['POST'])
def desplegar_x_alumnos():
    cantidad = int(request.form['cantidad'])
    conn = None  
    try:
        # AGREGAR DATOS FALSOS
        conn_fake = get_db_connection()  # Establecer conexión con base de datos falsa
        cursor_fake = conn_fake.cursor()

        # Generar e insertar registros falsos en la tabla alumno
        for i in range(cantidad):
            codigo_alu = f'{i+1}'
            cedula_alu = '0503121212'
            apellido_alu = 'Apellido'
            nombre_alu = 'eee'
            direccion_alu = 'aaa'
            telefono_alu = '0981234567'
            email_alu = ''
            genero_alu = random.choice(['Heterosexual', 'Homosexual'])
            fecha_nac_alu = '2002-03-05'
            observaciones_alu = ''

            sql_fake = ("INSERT INTO alumno (codigo_alu, cedula_alu, apellido_alu, nombre_alu, "
                        "direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
            values_fake = (codigo_alu, cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu)

            cursor_fake.execute(sql_fake, values_fake)

        # Confirmar y cerrar la conexión a la base de datos falsa
        conn_fake.commit()
        cursor_fake.close()
        conn_fake.close()

        # OBTENER DATOS REALES
        conn_real = get_db_connection()  # Establecer conexión con la base de datos real
        elapsed_time_sql = consulta_sql_normal(conn_real, cantidad)
        time.sleep(0.7)
        elapsed_time_sp = llamada_stored_procedure(conn_real, cantidad)
        conn_real.close()  # Cerrar la conexión

        return render_template('alumnosDesplegar.html', elapsed_time_sql=elapsed_time_sql, elapsed_time_sp=elapsed_time_sp)

    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al desplegar alumnos:", str(e))
        return "Error al desplegar alumnos: " + str(e), 500

    finally:
        if conn:
            conn.close()

def consulta_sql_normal(conn, cantidad):
    cursor = conn.cursor()
    start_time_sql = time.time()
    sql = "SELECT TOP (?) * FROM alumno"
    params = (cantidad,)
    cursor.execute(sql, params)
    alumnos = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in alumnos:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    elapsed_time_sql = time.time() - start_time_sql
    return elapsed_time_sql

def llamada_stored_procedure(conn, cantidad):
    cursor = conn.cursor()
    start_time_sp = time.time()
    sql = "EXEC sp_desplegar_x_alumnos ?"
    params = (cantidad,)
    cursor.execute(sql, params)
    alumnos = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in alumnos:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    elapsed_time_sp = time.time() - start_time_sp
    return elapsed_time_sp




# -- ALUMNOS: Eliminar los x desplegados
@app.route('/eliminar-registros-alumnos', methods=['POST'])
def eliminar_registros_alumnos():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Sentencia SQL para eliminar todos los registros de la tabla 'alumno'
        sql = "DELETE FROM alumno"

        cursor.execute(sql)
        conn.commit()

    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al eliminar registros de alumnos:", str(e))
        return "Error al eliminar registros de alumnos: " + str(e), 500

    finally:
        if conn:
            conn.close()

    return redirect(url_for('alumnos'))

# -- ALUMNOS: Eliminar
@app.route('/eliminar-alumno/<string:codigo_alu>')
def eliminar_alumno(codigo_alu):
    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Llama al stored procedure para eliminar el alumno
        cursor.execute("EXEC sp_eliminar_alumno ?", (codigo_alu,))
        conn.commit()
        cursor.close()
        return redirect(url_for('alumnos'))
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al eliminar el alumno:", str(e))
        return "Error al eliminar el alumno: " + str(e), 500
    finally:
        if conn:
            conn.close()

# -- ALUMNOS: Editar
@app.route('/editar-alumno/<string:codigo_alu>', methods=['POST'])
def editar_alumno(codigo_alu):
    conn = None
    try:
        # Recuperar los datos enviados desde el formulario de edición en el modal
        cedula_alu = request.form['cedula_alu']
        apellido_alu = request.form['apellido_alu']
        nombre_alu = request.form['nombre_alu']
        direccion_alu = request.form['direccion_alu']
        telefono_alu = request.form['telefono_alu']
        email_alu = request.form['email_alu']
        genero_alu = request.form['genero_alu']
        fecha_nac_alu = request.form['fecha_nac_alu']
        observaciones_alu = request.form['observaciones_alu']

        conn = get_db_connection()
        cursor = conn.cursor()
        # Llamar al stored procedure para editar el alumno
        sql = "EXEC sp_editar_alumno ?, ?, ?, ?, ?, ?, ?, ?, ?, ?"
        params = (codigo_alu, cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu)
        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
        return redirect(url_for('alumnos'))
    except Exception as e:
        print("Error al editar el alumno:", str(e))
        return "Error al editar el alumno: " + str(e), 500
    finally:
        if conn:
            conn.close()



# ---------- PROFESORES ----------
'''
# Ruta para agregar datos falsos de profesores (temporal, eliminar después de usar)
@app.route('/agregar-datos-falsos-profesores')
def agregar_datos_falsos_profesores():
    conn = None  # Inicializar la variable conn fuera del bloque try
    try:
        conn = get_db_connection()  # Asegúrate de tener la función get_db_connection() definida

        cursor = conn.cursor()

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
                   "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
            values = (codigo_pro, cedula_pro, apellido_pro, nombre_pro, titulo_pro, 
                      direccion_pro, telefono_pro, email_pro, genero_pro, fecha_nac_pro, observaciones_pro)

            cursor.execute(sql, values)

        # Confirma y cierra la conexión
        conn.commit()
        cursor.close()

        return redirect(url_for('profesores'))
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al agregar datos falsos de profesores:", str(e))
        return "Error al agregar datos falsos de profesores: " + str(e), 500
    finally:
        if conn:
            conn.close()
'''

@app.route('/profesores')
def profesores():
    return render_template('profesores.html')

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

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Llamada al stored procedure
        sql = "EXEC sp_agregar_profesor ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?"
        params = (codigo_pro, cedula_pro, apellido_pro, nombre_pro, titulo_pro, 
                  direccion_pro, telefono_pro, email_pro, genero_pro, fecha_nac_pro, observaciones_pro)
        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al agregar profesor:", str(e))
    finally:
        if conn:
            conn.close()
    return redirect(url_for('profesores'))

# -- PROFESORES: Buscar
@app.route('/buscar-profesores', methods=['POST'])
def buscar_profesores():
    start_time = time.time()
    busqueda = request.form['busqueda']
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Llamada al stored procedure
        sql = "EXEC sp_buscar_profesores ?"
        params = (busqueda,)
        cursor.execute(sql, params)

        # Recuperar resultados
        profesores = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in profesores:
            insertObject.append(dict(zip(columnNames, record)))

        cursor.close()
        elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
        elapsed_time_sec = int(elapsed_time)  # Extrae los segundos enteros
        elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000)  # Extrae los milisegundos

        return render_template('profesores.html', lista=insertObject, busqueda=busqueda, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)

    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al buscar profesores:", str(e))
        return "Error al buscar profesores: " + str(e), 500
    finally:
        if conn:
            conn.close()

# -- PROFESORES: Desplegar x profesores
@app.route('/desplegar-x-profesores', methods=['POST'])
def desplegar_x_profesores():
    start_time = time.time()
    cantidad = int(request.form['cantidad'])
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Llamada al stored procedure
        sql = "EXEC sp_desplegar_x_profesores ?"
        params = (cantidad,)
        cursor.execute(sql, params)

        # Recuperar resultados
        profesores = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in profesores:
            insertObject.append(dict(zip(columnNames, record)))

        cursor.close()
        elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
        elapsed_time_sec = int(elapsed_time)  # Extrae los segundos enteros
        elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000)  # Extrae los milisegundos

        return render_template('profesores.html', lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)

    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al desplegar profesores:", str(e))
        return "Error al desplegar profesores: " + str(e), 500
    finally:
        if conn:
            conn.close()

'''
@app.route('/mostrar-todos-profesores', methods=['POST'])
def mostrar_todos_profesores():
    start_time = time.time()  
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profesor")
        profesores = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in profesores:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
        elapsed_time = time.time() - start_time
        elapsed_time_sec = int(elapsed_time)
        elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000)  # Extrae los milisegundos
        
        return render_template('profesores.html', lista=insertObject, tiempo_respuesta=elapsed_time,
                               tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al mostrar todos los profesores:", str(e))
        return "Error al mostrar los profesores: " + str(e), 500
    finally:
        if conn:
            conn.close()
'''

# -- PROFESORES: Eliminar
@app.route('/eliminar-profesor/<string:codigo_pro>')
def eliminar_profesor(codigo_pro):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Llamada al stored procedure
        sql = "EXEC sp_eliminar_profesor ?"
        params = (codigo_pro,)
        cursor.execute(sql, params)

        # Confirmar la transacción
        conn.commit()
        cursor.close()

    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al eliminar el profesor:", str(e))
        return "Error al eliminar el profesor: " + str(e), 500
    finally:
        if conn:
            conn.close()

    return redirect(url_for('profesores'))

# -- PROFESORES: Editar
@app.route('/editar-profesor/<string:codigo_pro>', methods=['POST'])
def editar_profesor(codigo_pro):
    conn = None  
    try:
        # Obtener datos del formulario de edición en el modal
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

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Llamada al stored procedure
        sql = ("EXEC sp_editar_profesor ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?")
        params = (codigo_pro, cedula_pro, apellido_pro, nombre_pro, titulo_pro, direccion_pro, 
                  telefono_pro, email_pro, genero_pro, fecha_nac_pro, observaciones_pro)
        cursor.execute(sql, params)
        
        conn.commit()
        cursor.close()
    except Exception as e:
        print("Error al editar el profesor:", str(e))
        return "Error al editar el profesor: " + str(e), 500
    finally:
        if conn:
            conn.close()
    return redirect(url_for('profesores'))



# ---------- MATERIAS ----------
'''
# Ruta para agregar datos falsos de materias (temporal, eliminar después de usar)
@app.route('/agregar-datos-falsos-materias')
def agregar_datos_falsos_materias():
    conn = None  # Inicializar la variable conn fuera del bloque try
    try:
        conn = get_db_connection()  # Asegúrate de tener la función get_db_connection() definida

        cursor = conn.cursor()

        # Genera e inserta 100 registros en la tabla materia
        for i in range(100):
            codigo_mat = f'M{i+1}'  # Puedes ajustar la generación de códigos
            nombre_mat = fake.word()
            descripcion_mat = fake.word()
            horas_mat = random.randint(5, 13) * 15  # Ejemplo de generación aleatoria de horas
            creditos_mat = random.randint(1, 3)
            prerequisito_mat = fake.word()
            observaciones_mat = ''

            sql = ("INSERT INTO materia (codigo_mat, nombre_mat, descripcion_mat, horas_mat, creditos_mat, prerequisito_mat, observaciones_mat) "
                   "VALUES (?, ?, ?, ?, ?, ?, ?)")
            values = (codigo_mat, nombre_mat, descripcion_mat, horas_mat, creditos_mat, prerequisito_mat, observaciones_mat)

            cursor.execute(sql, values)

        # Confirma y cierra la conexión
        conn.commit()
        cursor.close()

        return redirect(url_for('materias'))
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al agregar datos falsos de materias:", str(e))
        return "Error al agregar datos falsos de materias: " + str(e), 500
    finally:
        if conn:
            conn.close()
'''

@app.route('/materias')
def materias():
    data = {
        'titulo': 'Materias',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    return render_template('materias.html', data=data)

# -- MATERIAS: Agregar
@app.route('/agregar-materia', methods=['POST'])
def agregar_materia():
    # Obtener datos del formulario
    codigo_mat = request.form['codigo_mat']
    nombre_mat = request.form['nombre_mat']
    descripcion_mat = request.form['descripcion_mat']
    horas_mat = request.form['horas_mat']
    creditos_mat = request.form['creditos_mat']
    prerequisito_mat = request.form['prerequisito_mat']
    observaciones_mat = request.form['observaciones_mat']

    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = ("INSERT INTO materia (codigo_mat, nombre_mat, descripcion_mat, horas_mat, creditos_mat, prerequisito_mat, observaciones_mat) "
               "VALUES (?, ?, ?, ?, ?, ?, ?)")
        params = (codigo_mat, nombre_mat, descripcion_mat, horas_mat, creditos_mat, prerequisito_mat, observaciones_mat)
        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al agregar materia:", str(e))
        return "Error al agregar materia: " + str(e), 500
    finally:
        if conn:
            conn.close()
    return redirect(url_for('materias'))

# -- MATERIAS: Buscar
@app.route('/buscar-materias', methods=['POST'])
def buscar_materias():
    start_time = time.time() 
    busqueda = request.form['busqueda']
    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM materia WHERE codigo_mat LIKE ?", ('%' + busqueda + '%',))
        materias = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in materias:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
        elapsed_time = time.time() - start_time # Calcula el tiempo transcurrido
        elapsed_time_sec = int(elapsed_time) # Extrae los segundos enteros
        elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000) # Extrae los milisegundos

        return render_template('materias.html', lista=insertObject, busqueda=busqueda, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al buscar materias:", str(e))
        return "Error al buscar materias: " + str(e), 500
    finally:
        if conn:
            conn.close()

# -- MATERIAS: Desplegar x
@app.route('/desplegar-x-materias', methods=['POST'])
def desplegar_x_materias():
    start_time = time.time() 

    cantidad = int(request.form['cantidad'])
    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT TOP {cantidad} * FROM materia")
        materias = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in materias:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
        elapsed_time = time.time() - start_time # Calcula el tiempo transcurrido
        elapsed_time_sec = int(elapsed_time) # Extrae los segundos enteros
        elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000) # Extrae los milisegundos

        return render_template('materias.html', lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al desplegar materias:", str(e))
        return "Error al desplegar materias: " + str(e), 500
    finally:
        if conn:
            conn.close()

@app.route('/mostrar-todas-materias', methods=['POST'])
def mostrar_todas_materias():
    start_time = time.time() 

    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM materia")
        materias = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in materias:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
        elapsed_time = time.time() - start_time # Calcula el tiempo transcurrido
        elapsed_time_sec = int(elapsed_time) # Extrae los segundos enteros
        elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000) # Extrae los milisegundos

        return render_template('materias.html', lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al mostrar todas las materias:", str(e))
        return "Error al mostrar las materias: " + str(e), 500
    finally:
        if conn:
            conn.close()

# -- MATERIAS: Eliminar
@app.route('/eliminar-materia/<string:codigo_mat>')
def eliminar_materia(codigo_mat):
    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM materia WHERE codigo_mat = ?", (codigo_mat,))
        conn.commit()
        cursor.close()
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al eliminar la materia:", str(e))
        return "Error al eliminar la materia: " + str(e), 500
    finally:
        if conn:
            conn.close()
    return redirect(url_for('materias'))

# -- MATERIAS: Editar
@app.route('/editar-materia/<string:codigo_mat>', methods=['POST'])
def editar_materia(codigo_mat):
    conn = None
    try:
        # Recuperar los datos enviados desde el formulario de edición en el modal
        nombre_mat = request.form['nombre_mat']
        descripcion_mat = request.form['descripcion_mat']
        horas_mat = request.form['horas_mat']
        creditos_mat = request.form['creditos_mat']
        prerequisito_mat = request.form['prerequisito_mat']
        observaciones_mat = request.form['observaciones_mat']

        conn = get_db_connection()
        cursor = conn.cursor()
        # Actualizar los atributos del registro en la base de datos
        sql = ("UPDATE materia SET nombre_mat = ?, descripcion_mat = ?, horas_mat = ?, "
               "creditos_mat = ?, prerequisito_mat = ?, observaciones_mat = ? WHERE codigo_mat = ?")
        params = (nombre_mat, descripcion_mat, horas_mat, creditos_mat, prerequisito_mat, observaciones_mat, codigo_mat)
        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
    except Exception as e:
        print("Error al editar la materia:", str(e))
        return "Error al editar la materia: " + str(e), 500
    finally:
        if conn:
            conn.close()
    return redirect(url_for('materias'))


# ---------- NOTAS ----------
@app.route('/notas')
def notas():
    data = {
        'titulo': 'Notas',
        'materia': 'Sistemas de bases de datos - NRC 14293'
    }
    return render_template('notas.html', data=data)

# -- NOTAS: Agregar
@app.route('/agregar-nota', methods=['POST'])
def agregar_nota():
    conn = None  
    try:
        codigo_not = request.form['codigo_not']
        nota1_not = request.form['nota1_not']
        nota2_not = request.form['nota2_not']
        nota3_not = request.form['nota3_not']
        fecha_not = request.form['fecha_not']
        observaciones_not = request.form['observaciones_not']
        codigo_alu = request.form['codigo_alu']
        codigo_pro = request.form['codigo_pro']
        codigo_mat = request.form['codigo_mat']

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = ("INSERT INTO nota (codigo_not, nota1_not, nota2_not, nota3_not, fecha_not, observaciones_not, codigo_alu, codigo_pro, codigo_mat) "
               "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
        cursor.execute(sql, (codigo_not, nota1_not, nota2_not, nota3_not, fecha_not, observaciones_not, codigo_alu, codigo_pro, codigo_mat))
        conn.commit()
        cursor.close()
        return redirect(url_for('notas'))
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al agregar nota:", str(e))
        return "Error al agregar nota: " + str(e), 500
    finally:
        if conn:
            conn.close()

# ---------- NOTAS: Buscar ----------
@app.route('/buscar-notas', methods=['POST'])
def buscar_notas():
    start_time = time.time()  
    conn = None  
    try:
        busqueda = request.form['busqueda']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nota WHERE codigo_not LIKE ?", ('%' + busqueda + '%',))
        notas = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in notas:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
        elapsed_time = time.time() - start_time
        elapsed_time_sec = int(elapsed_time)
        elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000)
        return render_template('notas.html', lista=insertObject, busqueda=busqueda, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al buscar notas:", str(e))
        return "Error al buscar notas: " + str(e), 500
    finally:
        if conn:
            conn.close()

@app.route('/desplegar-x-notas', methods=['POST'])
def desplegar_x_notas():
    conn = None  
    try:
        start_time = time.time()  
        cantidad = int(request.form['cantidad'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT TOP {cantidad} * FROM nota")
        notas = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in notas:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
        elapsed_time = time.time() - start_time
        elapsed_time_sec = int(elapsed_time)
        elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000)  # Extrae los milisegundos
        
        return render_template('notas.html', lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al desplegar notas:", str(e))
        return "Error al desplegar notas: " + str(e), 500
    finally:
        if conn:
            conn.close()

@app.route('/mostrar-todas-notas', methods=['POST'])
def mostrar_todas_notas():
    conn = None  
    try:
        start_time = time.time()  

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nota")
        notas = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in notas:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()

        elapsed_time = time.time() - start_time
        elapsed_time_sec = int(elapsed_time)
        elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000)  # Extrae los milisegundos
        return render_template('notas.html', lista=insertObject, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al mostrar todas las notas:", str(e))
        return "Error al mostrar las notas: " + str(e), 500
    finally:
        if conn:
            conn.close()

# -- NOTAS: Eliminar
@app.route('/eliminar-nota/<string:codigo_not>')
def eliminar_nota(codigo_not):
    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM nota WHERE codigo_not = ?"
        data = (codigo_not,)
        cursor.execute(sql, data)
        conn.commit()
        cursor.close()
        return redirect(url_for('notas'))
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al eliminar la nota:", str(e))
        return "Error al eliminar la nota: " + str(e), 500
    finally:
        if conn:
            conn.close()

# -- NOTAS: Editar
@app.route('/editar-nota/<string:codigo_not>', methods=['POST'])
def editar_nota(codigo_not):
    conn = None
    try:
        nota1_not = request.form['nota1_not']
        nota2_not = request.form['nota2_not']
        nota3_not = request.form['nota3_not']
        fecha_not = request.form['fecha_not']
        observaciones_not = request.form['observaciones_not']
        codigo_alu = request.form['codigo_alu']
        codigo_pro = request.form['codigo_pro']
        codigo_mat = request.form['codigo_mat']

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = ("UPDATE nota SET nota1_not = ?, nota2_not = ?, nota3_not = ?, fecha_not = ?, "
               "observaciones_not = ?, codigo_alu = ?, codigo_pro = ?, codigo_mat = ? WHERE codigo_not = ?")
        params = (nota1_not, nota2_not, nota3_not, fecha_not, observaciones_not, codigo_alu, codigo_pro, codigo_mat, codigo_not)
        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
        return redirect(url_for('notas'))
    except Exception as e:
        print("Error al editar la nota:", str(e))
        return "Error al editar la nota: " + str(e), 500
    finally:
        if conn:
            conn.close()



if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000)