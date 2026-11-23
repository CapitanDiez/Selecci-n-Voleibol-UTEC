import web
import logging

from mvc.controllers.login import Login
from mvc.controllers.cerrar_sesion import CerrarSesion
from mvc.controllers.index import Index
from mvc.controllers.lista_jugadores import ListaJugadores
from mvc.controllers.insertar_jugador import InsertarJugador
from mvc.controllers.cambiar_estado_jugador import CambiarEstadoJugador

logging.basicConfig(
    filename="aplicacion.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)

web.config.debug = False

urls = (
    '/login', 'Login',
    '/cerrar_sesion', 'CerrarSesion',
    '/', 'Index',
    '/lista_jugadores', 'ListaJugadores',
    '/insertar_jugador', 'InsertarJugador',
    '/cambiar_estado_jugador/(.*)', 'CambiarEstadoJugador',
)

app = web.application(urls, globals())

# Sesión de web.py (RTT05). Se guarda en web.config.sesion para usarla en todos los controladores
sesion = web.session.Session(
    app,
    web.session.DiskStore("sesiones"),
    initializer={"token": "", "email": "", "nombre": "", "rol": ""},
)
web.config.sesion = sesion

if __name__ == "__main__":
    app.run()
