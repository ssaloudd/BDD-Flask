from flask import Flask, render_template, request, url_for, redirect, session

from datetime import datetime
from faker import Faker #
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

# Función para obtener un usuario por su nombre de usuario
def obtener_usuario_por_nombre(nombre_usu):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuario WHERE nombre_usu = ?", (nombre_usu,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    return usuario
# Función para verificar si el usuario tiene permiso de acceso a una página específica
def verificar_permiso_usuario(usuario, permiso):
    if usuario[permiso]:
        return True
    else:
        return False

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
# Función para obtener los permisos de un usuario
def obtener_permisos_usuario(nombre_usu):
    usuario = obtener_usuario_por_nombre(nombre_usu)
    if usuario:
        return {
            'permisoAlumno_usu': usuario[3],  # Accede al cuarto elemento de la tupla
            'permisoProfesor_usu': usuario[4], # Accede al quinto elemento de la tupla
            'permisoMateria_usu': usuario[5],  # Accede al sexto elemento de la tupla
            'permisoNota_usu': usuario[6]       # Accede al séptimo elemento de la tupla
        }
    else:
        return None
    
@app.route('/permisos')
def permisos():
    # Verificar si el usuario ha iniciado sesión
    if 'username' in session:
        # Verificar si el usuario es "admin"
        if session['username'] == "admin":
            # Obtener los permisos del usuario actual
            permisos_usuario = obtener_permisos_usuario(session['username'])
            print(permisos_usuario)
            if permisos_usuario:
                return render_template('permisos.html', permisos=permisos_usuario)
            else:
                # Manejar el caso en el que no se puedan obtener los permisos del usuario
                return render_template('index.html', message="No se pudieron obtener los permisos del usuario.")
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

        # Obtener los valores de los permisos desde el formulario y convertirlos a booleanos
        permiso_alumno = 1 if 'permisoAlumno_usu' in request.form else 0
        permiso_profesor = 1 if 'permisoProfesor_usu' in request.form else 0
        permiso_materia = 1 if 'permisoMateria_usu' in request.form else 0
        permiso_nota = 1 if 'permisoNota_usu' in request.form else 0

        if nombre_usu and contrasena_usu:
            # Verificar si el nombre de usuario ya existe en la base de datos
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuario WHERE nombre_usu = ?", (nombre_usu,))
            existing_user = cursor.fetchone()

            if existing_user:
                # Si ya existe un usuario con el mismo nombre, mostrar un mensaje de error
                return "Error: El nombre de usuario ya está en uso. Por favor, elija otro.", 400
            
            # Si el nombre de usuario no existe, proceder a agregar el nuevo usuario
            sql_usuario = "INSERT INTO usuario (nombre_usu, contrasena_usu, permisoAlumno_usu, permisoProfesor_usu, permisoMateria_usu, permisoNota_usu) VALUES (?, ?, ?, ?, ?, ?)"
            params_usuario = (nombre_usu, contrasena_usu, permiso_alumno, permiso_profesor, permiso_materia, permiso_nota)
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
        sql = "DELETE FROM usuario WHERE id_usu=? AND id_usu != 1;"
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

        # Obtener los valores de los permisos desde el formulario y convertirlos a booleanos
        permiso_alumno = 1 if 'permisoAlumno_usu' in request.form else 0
        permiso_profesor = 1 if 'permisoProfesor_usu' in request.form else 0
        permiso_materia = 1 if 'permisoMateria_usu' in request.form else 0
        permiso_nota = 1 if 'permisoNota_usu' in request.form else 0

        # Verificar si el nombre de usuario ya existe en la base de datos, excluyendo el usuario actual
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario WHERE nombre_usu = ? AND id_usu != ?", (nombre_usu, id_usu))
        existing_user = cursor.fetchone()

        if existing_user:
            # Si ya existe un usuario con el mismo nombre, mostrar un mensaje de error
            return "Error: El nombre de usuario ya está en uso. Por favor, elija otro.", 400

        # Si el nombre de usuario no existe, proceder a actualizar el usuario
        sql = "UPDATE usuario SET nombre_usu=?, contrasena_usu=?, permisoAlumno_usu=?, permisoProfesor_usu=?, permisoMateria_usu=?, permisoNota_usu=? WHERE id_usu=?"
        params = (nombre_usu, contrasena_usu, permiso_alumno, permiso_profesor, permiso_materia, permiso_nota, id_usu)
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
@app.route('/alumnos')
def alumnos():
    # Verificar si el usuario ha iniciado sesión
    if 'username' in session:
        # Obtener el usuario de la base de datos
        usuario = obtener_usuario_por_nombre(session['username'])
        print("Usuario:", usuario)
        # Verificar el permiso del usuario para acceder a la página de alumnos
        if verificar_permiso_usuario(usuario, 3):
            return render_template('alumnos.html')
        else:
            # Redirigir al usuario al index.html si no tiene permiso
            return render_template('index.html', message="No tienes permiso para acceder a esta página.")
    else:
        # Redirigir al usuario al inicio de sesión si no ha iniciado sesión
        return redirect(url_for('login'))

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
@app.route('/profesores')
def profesores():
    # Verificar si el usuario ha iniciado sesión
    if 'username' in session:
        # Obtener el usuario de la base de datos
        usuario = obtener_usuario_por_nombre(session['username'])
        
        # Verificar el permiso del usuario para acceder a la página de profesores
        if verificar_permiso_usuario(usuario, 4):
            return render_template('profesores.html')
        else:
            # Redirigir al usuario al index.html si no tiene permiso
            return render_template('index.html', message="No tienes permiso para acceder a esta página.")
    else:
        # Redirigir al usuario al inicio de sesión si no ha iniciado sesión
        return redirect(url_for('login'))

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
@app.route('/materias')
def materias():
    # Verificar si el usuario ha iniciado sesión
    if 'username' in session:
        # Obtener el usuario de la base de datos
        usuario = obtener_usuario_por_nombre(session['username'])
        
        # Verificar el permiso del usuario para acceder a la página de materias
        if verificar_permiso_usuario(usuario, 5):  # El número 5 corresponde a la columna 'permisoMateria_usu'
            return render_template('materias.html')
        else:
            # Redirigir al usuario al index.html si no tiene permiso
            return render_template('index.html', message="No tienes permiso para acceder a esta página.")
    else:
        # Redirigir al usuario al inicio de sesión si no ha iniciado sesión
        return redirect(url_for('login'))

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
    # Verificar si el usuario ha iniciado sesión
    if 'username' in session:
        # Obtener el usuario de la base de datos
        usuario = obtener_usuario_por_nombre(session['username'])
        
        # Verificar el permiso del usuario para acceder a la página de notas
        if verificar_permiso_usuario(usuario, 6):  # El número 6 corresponde a la columna 'permisoNota_usu'
            return render_template('notas.html')
        else:
            # Redirigir al usuario al index.html si no tiene permiso
            return render_template('index.html', message="No tienes permiso para acceder a esta página.")
    else:
        # Redirigir al usuario al inicio de sesión si no ha iniciado sesión
        return redirect(url_for('login'))

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