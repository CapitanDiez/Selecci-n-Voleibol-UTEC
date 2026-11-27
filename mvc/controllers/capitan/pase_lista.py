import web
from mvc.helpers import sesion
from mvc.helpers.auth import requiere_rol
from mvc.helpers.formularios import entero, registros_asistencia
from mvc.helpers.vistas import pagina
from mvc.models.comun import model_asistencias, model_entrenamientos


class PaseLista:
    def _mostrar(self, entrenamiento_id, error=None, mensaje=None):
        rama = sesion.rama()
        entrenamientos = model_entrenamientos.recientes_y_proximos(rama)
        entrenamiento, jugadores = None, []
        if entrenamiento_id:
            entrenamiento = model_entrenamientos.obtener(entrenamiento_id)
            if entrenamiento and entrenamiento.rama == rama:
                jugadores = model_asistencias.jugadores_para_lista(rama)  # RF-03
            else:
                entrenamiento = None
        return pagina("capitan", "pase_lista", "Pase de lista", entrenamientos, entrenamiento, jugadores,
                      error, mensaje, rama)

    @requiere_rol("capitan")
    def GET(self):
        f = web.input(entrenamiento_id="")
        return self._mostrar(entero(f.entrenamiento_id))

    @requiere_rol("capitan")
    def POST(self):
        f = web.input(entrenamiento_id="")
        eid = entero(f.entrenamiento_id)
        jugadores = model_asistencias.jugadores_para_lista(sesion.rama())
        ok, msg = model_asistencias.guardar(eid, registros_asistencia(f, jugadores))  # RF-05 + RF-14
        return self._mostrar(eid, None if ok else msg, msg if ok else None)
