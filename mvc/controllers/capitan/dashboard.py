from mvc.helpers import sesion
from mvc.helpers.auth import requiere_rol
from mvc.helpers.vistas import pagina


class Dashboard:
    @requiere_rol("capitan")
    def GET(self):
        return pagina("capitan", "dashboard", "Inicio", sesion.usuario(), sesion.rama())
