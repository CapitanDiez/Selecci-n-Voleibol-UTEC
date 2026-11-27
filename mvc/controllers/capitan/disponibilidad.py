import web
from mvc.helpers import sesion
from mvc.helpers.auth import requiere_rol
from mvc.helpers.formularios import entero
from mvc.helpers.vistas import pagina
from mvc.models.capitan import model_disponibilidad
from mvc.models.comun import model_jugadores, model_partidos


class Disponibilidad:
    def _mostrar(self, partido_id, error=None, mensaje=None):
        rama = sesion.rama()
        partidos = model_partidos.proximos_liga(rama)
        partido = model_partidos.obtener(partido_id) if partido_id else None
        if partido and partido.rama != rama:
            partido = None
        jugadores = model_jugadores.listar(rama, solo_activos=True) if partido else []
        actuales = model_disponibilidad.actuales(partido.id) if partido else {}
        limite = model_disponibilidad.sabado_limite(partido.fecha) if partido else None
        return pagina("capitan", "disponibilidad", "Disponibilidad", partidos, partido, jugadores, actuales,
                      limite, rama, error, mensaje)

    @requiere_rol("capitan")
    def GET(self):
        f = web.input(partido_id="")
        return self._mostrar(entero(f.partido_id))

    @requiere_rol("capitan")
    def POST(self):  # RF-16
        f = web.input(partido_id="")
        pid = entero(f.partido_id)
        jugadores = model_jugadores.listar(sesion.rama(), solo_activos=True)
        respuestas = {j.id: f.get("disp_%s" % j.id) == "si" for j in jugadores}
        ok, msg = model_disponibilidad.guardar(pid, respuestas)
        return self._mostrar(pid, None if ok else msg, msg if ok else None)
