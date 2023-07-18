from conexion import ConexionDB

def crear_tabla_usuarios():
    conexion = ConexionDB()
    sql = '''
    CREATE TABLE USUARIOS(
        ID_USUARIO INTEGER NOT NULL,
        NUMERO VARCHAR(18)
        ID_HORA DATETIME,
        PRIMARY KEY(ID_USUARIO AUTOINCREMENT)
    )
    '''
    try:
        conexion.cursor.execute(sql)
        conexion.cerrar()
        print('Se ha creado exitosamente la tabla')
    except Exception as error:
        print(error)


def crear_tabla_horas():
    conexion = ConexionDB()
    sql = '''
    CREATE TABLE HORAS(
        ID_HORA INTEGER NOT NULL,
        HORA DATETIME,
        DIRECCION VARCHAR(255),
        PRIMARY KEY(ID_USUARIO AUTOINCREMENT)
    )
    '''
    try:
        conexion.cursor.execute(sql)
        conexion.cerrar()
        print('Se ha creado exitosamente la tabla')
    except Exception as error:
        print(error)

def borrar_tabla():
    conexion = ConexionDB()
    sql = 'DROP TABLE HORAS'
    try:
        conexion.cursor.execute(sql)
        conexion.cerrar()
        print('Se ha borrado la tabla con exito')
    except Exception as error:
        print(error)

def guardar_usuario(id_user,id_hour):
    conexion = ConexionDB()
    sql = f'''
    INSERT INTO USUARIOS VALUES ({id_user},{id_hour})
    '''
    try:
        conexion.cursor.execute(sql)
        conexion.cerrar()
        print('Se ha creado exitosamente la tabla')
    except Exception as error:
        print(error)