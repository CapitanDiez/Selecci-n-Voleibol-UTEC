import web
import logging
from mvc.models.model_sesiones import ModelSesiones

logger = logging.getLogger(__name__)

render = web.template.render("mvc/views", base="template", globals={"web": web})


class Index:
    """Página de bienvenida después de iniciar sesión."""

    def GET(self):
        # RNT01: valida la sesión antes de ejecutar
        if not ModelSesiones().sesionValida():
            raise web.seeother("/login")

        return render.index()  # type: ignore
