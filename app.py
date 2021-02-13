"""

  ____          _____               _ _           _       
 |  _ \        |  __ \             (_) |         | |      
 | |_) |_   _  | |__) |_ _ _ __ _____| |__  _   _| |_ ___ 
 |  _ <| | | | |  ___/ _` | '__|_  / | '_ \| | | | __/ _ \
 | |_) | |_| | | |  | (_| | |   / /| | |_) | |_| | ||  __/
 |____/ \__, | |_|   \__,_|_|  /___|_|_.__/ \__, |\__\___|
         __/ |                               __/ |        
        |___/                               |___/         
    
____________________________________
/ Si necesitas ayuda, contáctame en \
\ https://parzibyte.me               /
 ------------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
Creado por Parzibyte (https://parzibyte.me).
------------------------------------------------------------------------------------------------
Si el código es útil para ti, puedes agradecerme siguiéndome: https://parzibyte.me/blog/sigueme/
Y compartiendo mi blog con tus amigos
También tengo canal de YouTube: https://www.youtube.com/channel/UCroP4BTWjfM0CkGB6AFUoBg?sub_confirmation=1
------------------------------------------------------------------------------------------------
"""

import cv2
import utiles
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

# Si tienes varias cámaras puedes acceder a ellas en 1, 2, etcétera (en lugar de 0)
camara = cv2.VideoCapture(0)

"""
    Configuraciones de vídeo
"""
FRAMES_VIDEO = 20.0
RESOLUCION_VIDEO = (640, 480)
# Marca de agua
# https://docs.opencv.org/master/d6/d6e/group__imgproc__draw.html#ga5126f47f883d730f633d74f07456c576
UBICACION_FECHA_HORA = (0, 15)
FUENTE_FECHA_Y_HORA = cv2.FONT_HERSHEY_PLAIN
ESCALA_FUENTE = 1
COLOR_FECHA_HORA = (255, 255, 255)
GROSOR_TEXTO = 1
TIPO_LINEA_TEXTO = cv2.LINE_AA
# El código de 4 dígitos. En windows me parece que se soporta el XVID
fourcc = cv2.VideoWriter_fourcc(*'XVID')
archivo_video = None
grabando = False


def agregar_fecha_hora_frame(frame):
    cv2.putText(frame, utiles.fecha_y_hora(), UBICACION_FECHA_HORA, FUENTE_FECHA_Y_HORA,
                ESCALA_FUENTE, COLOR_FECHA_HORA, GROSOR_TEXTO, TIPO_LINEA_TEXTO)


# Una función generadora para stremear la cámara
# https://flask.palletsprojects.com/en/1.1.x/patterns/streaming/


def generador_frames():
    while True:
        ok, imagen = obtener_frame_camara()
        if not ok:
            break
        else:
            # Regresar la imagen en modo de respuesta HTTP
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + imagen + b"\r\n"


def obtener_frame_camara():
    ok, frame = camara.read()
    if not ok:
        return False, None
    agregar_fecha_hora_frame(frame)
    # Escribir en el vídeo en caso de que se esté grabando
    if grabando and archivo_video is not None:
        archivo_video.write(frame)
    # Codificar la imagen como JPG
    _, bufer = cv2.imencode(".jpg", frame)
    imagen = bufer.tobytes()

    return True, imagen


# Cuando visiten la ruta
@app.route("/streaming_camara")
def streaming_camara():
    return Response(generador_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Cuando toman la foto
@app.route("/tomar_foto_descargar")
def descargar_foto():
    ok, frame = obtener_frame_camara()
    if not ok:
        abort(500)
        return
    respuesta = Response(frame)
    respuesta.headers["Content-Type"] = "image/jpeg"
    respuesta.headers["Content-Transfer-Encoding"] = "Binary"
    respuesta.headers["Content-Disposition"] = "attachment; filename=\"foto.jpg\""
    return respuesta


@app.route("/tomar_foto_guardar")
def guardar_foto():
    nombre_foto = utiles.obtener_uuid() + ".jpg"
    ok, frame = camara.read()
    if ok:
        agregar_fecha_hora_frame(frame)
        cv2.imwrite(nombre_foto, frame)
    return jsonify({
        "ok": ok,
        "nombre_foto": nombre_foto,
    })


# Cuando visiten /, servimos el index.html
@app.route('/')
def index():
    return render_template("index.html")


@app.route("/comenzar_grabacion")
def comenzar_grabacion():
    global grabando
    global archivo_video
    if grabando and archivo_video:
        return jsonify(False)
    nombre = utiles.fecha_y_hora_para_nombre_archivo() + ".avi"
    archivo_video = cv2.VideoWriter(
        nombre, fourcc, FRAMES_VIDEO, RESOLUCION_VIDEO)
    grabando = True
    return jsonify(True)


@app.route("/detener_grabacion")
def detener_grabacion():
    global grabando
    global archivo_video
    if not grabando or not archivo_video:
        return jsonify(False)
    grabando = False
    archivo_video.release()
    archivo_video = None
    return jsonify(True)


@app.route("/estado_grabacion")
def estado_grabacion():
    return jsonify(grabando)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
