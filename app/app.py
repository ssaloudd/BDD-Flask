from flask import Flask, render_template, request, url_for, redirect, session
#from flask_mysqldb import MySQL

from datetime import datetime
from faker import Faker #
import random #
import time #
import pyodbc
fake = Faker()
import os

app=Flask(__name__)

# Configuración de conexión a SQL Server con Windows Authentication
server = 'DESKTOP-PAQ11B3'
database = 'escolastico1'
driver = '{ODBC Driver 17 for SQL Server}'
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

# Función para establecer la conexión a la base de datos
def get_db_connection():
    return pyodbc.connect(conn_str)

app.secret_key = os.urandom(24)
# ---------- LOGIN ----------
@app.route('/', methods=['GET', 'POST'])
def login():
    error_msg = None

    if request.method == 'POST':
        nombre_usu = request.form['nombre_usu']
        contrasena_usu = request.form['contrasena_usu']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuario WHERE nombre_usu = ?", (nombre_usu,))
            user = cursor.fetchone()

            if user:
                # Convertir la fila en un diccionario para facilitar el acceso por nombre de columna
                user_dict = dict(zip([column[0] for column in cursor.description], user))
                if user_dict['contrasena_usu'] == contrasena_usu:
                    session['username'] = nombre_usu
                    return redirect(url_for('index'))
                else:
                    error_msg = "Contraseña incorrecta. Por favor, inténtalo de nuevo."
            else:
                error_msg = "Usuario no encontrado. Por favor, verifica tu nombre de usuario y contraseña."
        except Exception as e:
            error_msg = "Error al iniciar sesión: " + str(e)
        finally:
            if conn:
                conn.close()

    return render_template('login.html', error=error_msg)

# ---------- INICIO ----------
@app.route('/index')
def index():
    return render_template('index.html')

# ---------- PERMISOS ----------
@app.route('/permisos')
def permisos():
    # Verificar si el usuario ha iniciado sesión
    if 'username' in session:
        # Verificar si el usuario es "admin"
        if session['username'] == "admin":
            return render_template('permisos.html')
        else:
            # Redirigir a otra página o mostrar un mensaje de error
            return render_template('index.html', message="No tienes permiso para acceder a esta página.")
    else:
        # Redirigir al usuario al inicio de sesión si no ha iniciado sesión
        return redirect(url_for('login'))

# -- PERMISOS: Agregar
@app.route('/agregar-usuario', methods=['POST'])
def agregar_usuario():
    conn = None  
    try:
        nombre_usu = request.form['nombre_usu']
        contrasena_usu = request.form['contrasena_usu']

        if nombre_usu and contrasena_usu:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Agregar usuario a la tabla 'usuario'
            sql_usuario = "INSERT INTO usuario (nombre_usu, contrasena_usu) VALUES (?, ?)"
            params_usuario = (nombre_usu, contrasena_usu)
            cursor.execute(sql_usuario, params_usuario)

            conn.commit()
            cursor.close()
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al agregar usuario:", str(e))
    finally:
        if conn:  # Verificar si la variable está definida antes de intentar cerrarla
            conn.close()
    return redirect(url_for('permisos'))

# -- PERMISOS: Mostrar usuarios
@app.route('/mostrar-todos-usuarios', methods=['POST'])
def mostrar_todos_usuarios():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario")
        usuarios = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in usuarios:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()

        return render_template('permisos.html', lista=insertObject)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al mostrar todos los usuarios:", str(e))
        return "Error al mostrar los usuarios: " + str(e), 500
    finally:
        if conn:
            conn.close()

# -- PERMISOS: Eliminar
@app.route('/eliminar-usuario/<int:id_usu>')
def eliminar_usuario(id_usu):
    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM usuario WHERE id_usu=?"
        data = (id_usu,)
        cursor.execute(sql, data)
        conn.commit()
        cursor.close()
        return redirect(url_for('permisos'))
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al eliminar el usuario:", str(e))
        return "Error al eliminar el usuario: " + str(e), 500
    finally:
        if conn:
            conn.close()

# -- PERMISOS: Editar
@app.route('/editar-usuario/<int:id_usu>', methods=['POST'])
def editar_usuario(id_usu):
    conn = None
    try:
        # Recuperar los datos enviados desde el formulario de edición
        nombre_usu = request.form['nombre_usu']
        contrasena_usu = request.form['contrasena_usu']

        conn = get_db_connection()
        cursor = conn.cursor()
        # Actualizar los atributos del registro en la base de datos
        sql = "UPDATE usuario SET nombre_usu=?, contrasena_usu=? WHERE id_usu=?"
        params = (nombre_usu, contrasena_usu, id_usu)
        cursor.execute(sql, params)

        conn.commit()
        cursor.close()
        return redirect(url_for('permisos'))
    except Exception as e:
        print("Error al editar el usuario:", str(e))
        return "Error al editar el usuario: " + str(e), 500
    finally:
        if conn:
            conn.close()




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
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Agregar alumno a la tabla 'alumno'
            sql_alumno = "INSERT INTO alumno (codigo_alu, cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            params_alumno = (codigo_alu, cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu)  # Recupera el nombre de usuario de la sesión
            cursor.execute(sql_alumno, params_alumno)

            # Agregar alumno a la tabla 'alumnoback'
            sql_alumnoback = "INSERT INTO alumnoback (codigo_alubk, cedula_alubk, apellido_alubk, nombre_alubk, direccion_alubk, telefono_alubk, email_alubk, genero_alubk, fecha_nac_alubk, observaciones_alubk, usuarioInsert_alubk, fechaInsert_alubk) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            params_alumnoback = (codigo_alu, cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu, session.get('username', 'unknown'), datetime.now())
            cursor.execute(sql_alumnoback, params_alumnoback)

            conn.commit()
            cursor.close()
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al agregar alumno:", str(e))
    finally:
        if conn:  # Verificar si la variable está definida antes de intentar cerrarla
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
        cursor.execute("SELECT * FROM alumno WHERE codigo_alu LIKE ?", ('%'+busqueda+'%',))
        alumnos = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in alumnos:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()

        return render_template('alumnos.html', lista=insertObject, busqueda=busqueda)
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
    start_time = time.time()  
    cantidad = int(request.form['cantidad'])
    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT TOP {cantidad} * FROM alumno")
        alumnos = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in alumnos:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
        
        return render_template('alumnos.html', lista=insertObject)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al desplegar alumnos:", str(e))
        return "Error al desplegar alumnos: " + str(e), 500
    finally:
        if conn:
            conn.close()

# -- ALUMNOS: Mostrar todos
@app.route('/mostrar-todos-alumnos', methods=['POST'])
def mostrar_todos_alumnos():
    start_time = time.time()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alumno")
        alumnos = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in alumnos:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()

        return render_template('alumnos.html', lista=insertObject)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al mostrar todos los alumnos:", str(e))
        return "Error al mostrar los alumnos: " + str(e), 500
    finally:
        if conn:
            conn.close()

# -- ALUMNOS: Eliminar
@app.route('/eliminar-alumno/<string:codigo_alu>')
def eliminar_alumno(codigo_alu):
    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM alumno WHERE codigo_alu=?"
        data = (codigo_alu,)
        cursor.execute(sql, data)
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
        # Actualizar los atributos del registro en la base de datos
        sql = "UPDATE alumno SET cedula_alu=?, apellido_alu=?, nombre_alu=?, direccion_alu=?, telefono_alu=?, email_alu=?, genero_alu=?, fecha_nac_alu=?, observaciones_alu=? WHERE codigo_alu=?"
        params = (cedula_alu, apellido_alu, nombre_alu, direccion_alu, telefono_alu, email_alu, genero_alu, fecha_nac_alu, observaciones_alu, codigo_alu)
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
        sql = ("INSERT INTO profesor (codigo_pro, cedula_pro, apellido_pro, nombre_pro, "
               "titulo_pro, direccion_pro, telefono_pro, email_pro, genero_pro, fecha_nac_pro, observaciones_pro) "
               "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
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
        cursor.execute("SELECT * FROM profesor WHERE codigo_pro LIKE ?", ('%'+busqueda+'%',))
        profesores = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in profesores:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
        elapsed_time = time.time() - start_time # Calcula el tiempo transcurrido
        elapsed_time_sec = int(elapsed_time) # Extrae los segundos enteros
        elapsed_time_ms = float((elapsed_time - elapsed_time_sec) * 1000) # Extrae los milisegundos

        return render_template('profesores.html', lista=insertObject, busqueda=busqueda, tiempo_respuesta=elapsed_time, tiempo_sec=elapsed_time_sec, tiempo_ms=elapsed_time_ms)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al buscar profesores:", str(e))
        return "Error al buscar profesores: " + str(e), 500
    finally:
        if conn:
            conn.close()

@app.route('/desplegar-x-profesores', methods=['POST'])
def desplegar_x_profesores():
    start_time = time.time() 

    cantidad = int(request.form['cantidad'])
    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT TOP {cantidad} * FROM profesor")
        profesores = cursor.fetchall()
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in profesores:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()

        return render_template('profesores.html', lista=insertObject)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al desplegar profesores:", str(e))
        return "Error al desplegar profesores: " + str(e), 500
    finally:
        if conn:
            conn.close()

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
        
        return render_template('profesores.html', lista=insertObject)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al mostrar todos los profesores:", str(e))
        return "Error al mostrar los profesores: " + str(e), 500
    finally:
        if conn:
            conn.close()

# -- PROFESORES: Eliminar
@app.route('/eliminar-profesor/<string:codigo_pro>')
def eliminar_profesor(codigo_pro):
    conn = None  
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM profesor WHERE codigo_pro = ?", [codigo_pro])
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
        # Actualizar los atributos del registro en la base de datos
        sql = ("UPDATE profesor SET cedula_pro = ?, apellido_pro = ?, nombre_pro = ?, "
               "titulo_pro = ?, direccion_pro = ?, telefono_pro = ?, email_pro = ?, "
               "genero_pro = ?, fecha_nac_pro = ?, observaciones_pro = ? WHERE codigo_pro = ?")
        params = (cedula_pro, apellido_pro, nombre_pro, titulo_pro, direccion_pro, 
                  telefono_pro, email_pro, genero_pro, fecha_nac_pro, observaciones_pro, codigo_pro)
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
    return render_template('materias.html')

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

        return render_template('materias.html', lista=insertObject)
    except Exception as e:
        # Manejar el error apropiadamente
        print("Error al desplegar materias:", str(e))
        return "Error al desplegar materias: " + str(e), 500
    finally:
        if conn:
            conn.close()

# -- MATERIAS: Mostrar todo
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

        return render_template('materias.html', lista=insertObject)
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

# -- NOTAS: Buscar
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

# -- NOTAS: Desplegar x
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
        
        return render_template('notas.html', lista=insertObject)
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

        return render_template('notas.html', lista=insertObject)
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