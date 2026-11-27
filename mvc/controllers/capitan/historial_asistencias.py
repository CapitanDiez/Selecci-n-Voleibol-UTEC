import web
from mvc.helpers import fechas, sesion
from mvc.helpers.auth import requiere_rol
from mvc.helpers.vistas import pagina
from mvc.models.comun import model_asistencias


class HistorialAsistencias:
    @requiere_rol("capitan")
    def GET(self):
        f = web.input(desde="", hasta="")
        desde, hasta = fechas.rango(f.desde, f.hasta)
        rama = sesion.rama()
        filas = model_asistencias.historial(rama, desde, hasta)
        return pagina("capitan", "historial_asistencias", "Historial de asistencias", filas, desde, hasta, rama)
