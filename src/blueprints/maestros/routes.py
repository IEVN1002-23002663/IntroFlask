from flask import Blueprint,jsonify,request
from database import mysql
 
maestros_bp = Blueprint(
    'maestros  ',
    __name__,
    url_prefix='/api/maestros'
)
 
 
def fila_a_diccionario(cursor, fila):
    columnas=[columna[0] for columna in cursor.description]
    return dict(zip(columnas,fila))

@maestros_bp.route("/",methods=['GET'])
def lista_maestros():
    try:
        cursor=mysql.connection.cursor()
        sql="select * from maestros"
        cursor.execute(sql)
        datos=cursor.fetchall()
        maestros=[]
        for fila in datos:
            maestro={"matricula":fila[0],"nombre":fila[1],
                    "apaterno":fila[2],"amaterno":fila[3],
                    "correo":fila[4]}
            maestros.append(maestro)
        return  jsonify({'maestros':maestros,'mensaje':'Lista de maestros',
                         'exito':True})
    except Exception as ex:
        return jsonify({"message": "error {}".format(ex),'exito':False})
 
@maestros_bp.route("/<string:matricula>",methods=['GET'])
def leer_maestro(matricula):
    cursor=None
    try:
        cursor=mysql.connection.cursor()
        cursor.execute("""SELECT * FROM maestros WHERE
        matricula=%s""",(matricula,))
        fila=cursor.fetchone()
        if fila is None:
            return jsonify({
                'mensaje':'Maestro no encontrado',
                'exito':False
            }),404
        maestro=fila_a_diccionario(cursor,fila)
        return jsonify({
            'maestro':maestro,
            'exito':True
        }),200
    except Exception as ex:
        return jsonify({
            'mensaje':'Error al consultar el maestro {}'.format(ex),
            'exito':False
        }),500
    finally:
        if cursor is not None:
            cursor.close()
 
 
#POST:Registrar un maestro
@maestros_bp.route('/', methods=['POST'])
def registrar_maestro():
    datos = request.get_json(silent=True)
 
    if not isinstance(datos, dict):
        return jsonify({
            'mensaje': 'Se requiere un objeto JSON',
            'exito': False
        }), 400
 
    campos = [
        'matricula', 'nombre', 'apaterno',
        'amaterno', 'correo'
    ]
 
    if any(
        campo not in datos
        or not isinstance(datos[campo], str)
        or not datos[campo].strip()
        for campo in campos
    ):
        return jsonify({
            'mensaje': 'Faltan campos obligatorios o son inválidos',
            'exito': False
        }), 400
 
    cursor = None
 
    try:
        cursor = mysql.connection.cursor()
 
        # Comprobar si la matrícula ya existe
        cursor.execute(
            "SELECT matricula FROM maestros WHERE matricula = %s",
            (datos['matricula'].strip(),)
        )
 
        if cursor.fetchone() is not None:
            return jsonify({
                'mensaje': 'La matrícula ya existe',
                'exito': False
            }), 409
 
        # Insertar el registro con parámetros SQL
        cursor.execute("""
            INSERT INTO maestros
                (matricula, nombre, apaterno, amaterno, correo)
            VALUES (%s, %s, %s, %s, %s)
        """, tuple(datos[campo].strip() for campo in campos))
 
        mysql.connection.commit()
 
        return jsonify({
            'mensaje': 'Maestro registrado correctamente',
            'exito': True
        }), 201
 
    except Exception as ex:
        mysql.connection.rollback()
 
        return jsonify({
            'mensaje': 'Error al registrar el maestro: {}'.format(ex),
            'exito': False
        }), 500
 
    finally:
        if cursor is not None:
            cursor.close()
 
 
@maestros_bp.route("/<string:matricula>",methods=['PUT'])
def modificar_maestro(matricula):
    datos=request.get_json()
    if not datos:
        return jsonify({
            "mensaje": "No se recibieron datos para modificar"
        }), 400
 
    nombre=datos.get('nombre')
    apaterno=datos.get('apaterno')
    amaterno=datos.get('amaterno')
    correo=datos.get('correo')
 
    if not nombre or not apaterno or not correo:
        return jsonify({
            "mensaje": "Nombre, apellido paterno y correo son obligatorios"
        }), 400
    cursor=None
    try:
        cursor=mysql.connection.cursor()
        cursor.execute(
            "SELECT matricula FROM maestros WHERE matricula=%s",
            (matricula,)
        )
        maestro=cursor.fetchone()
        if not maestro:
           return  jsonify({
            "mensaje": "No existe un maestro con esa matricula"
        }), 404
 
        sql="""
            UPDATE maestros
            SET nombre=%s,
                apaterno=%s,
                amaterno=%s,
                correo=%s
            WHERE matricula=%s
         """
        cursor.execute(sql,(
            nombre,
            apaterno,
            amaterno,
            correo,
            matricula
        ))
        mysql.connection.commit()
        return  jsonify({
            "mensaje": "Maestro modificado correctamente",
            "matricula":matricula
        }), 200
 
    except Exception as e:
        mysql.connection.rollback()
 
        return jsonify({
            "mensaje": "Error al modificar el maestro",
            "error": str(e)
        }), 500
 
    finally:
        if cursor:
            cursor.close()
 
@maestros_bp.route("/<string:matricula>",methods=['DELETE'])
def eliminar_maestro(matricula):
    cursor=None
    try:
        cursor=mysql.connection.cursor()
        cursor.execute(
            "SELECT matricula FROM maestros WHERE matricula = %s",
            (matricula,)
        )
        maestro=cursor.fetchone()
        if not maestro:
            return jsonify({
                "mensaje": "No existe un maestro con esa matrícula"
            }), 404
        cursor.execute(
            "DELETE FROM maestros WHERE matricula =%s ",
            (matricula,)
        )
        mysql.connection.commit()
        return jsonify({
            "mensaje": "Maestro eliminado correctamente",
            "matricula": matricula
        }), 200
 
    except Exception as e:
        mysql.connection.rollback()
 
        return jsonify({
            "mensaje": "Error al eliminar el maestro",
            "error": str(e)
        }), 500
 
    finally:
        if cursor:
            cursor.close()