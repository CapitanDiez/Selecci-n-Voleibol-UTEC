import web
from mvc.helpers import sesion
from mvc.helpers.auth import requiere_rol
from mvc.helpers.vistas import pagina
from mvc.models.comun import model_jugadores


class InsertarJugador:
    @requiere_rol("capitan")
    def GET(self):
        return pagina("capitan", "jugador_form", "Agregar jugador", [], {}, sesion.rama())

    @requiere_rol("capitan")
    def POST(self):
        datos = dict(web.input(nombre="", matricula="", correo="", telefono="", edad="", cuatrimestre="",
                               carrera="", rama=sesion.rama(), posicion="", numero_playera=""))
        ok, resultado = model_jugadores.crear(datos)  # RF-02 + RF-11
        if ok:
            raise web.seeother("/capitan/jugadores?mensaje=Jugador+guardado+correctamente")
        return pagina("capitan", "jugador_form", "Agregar jugador", resultado, datos, sesion.rama())
