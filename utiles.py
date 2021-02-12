import uuid

from datetime import datetime


def obtener_uuid():
    return str(uuid.uuid4())


def fecha_y_hora():
    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d %H:%M:%S | https://parzibyte.me/blog")
    return fecha


def fecha_y_hora_para_nombre_archivo():
    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d_%H-%M-%S")
    return fecha