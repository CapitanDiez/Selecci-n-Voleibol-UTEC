import web
import logging
from mvc.models.auth_users import AuthUsers

logger = logging.getLogger(__name__)

render_login = web.template.render("mvc/views")
render = web.template.render("mvc/views", base="template", globals={"web": web})


class Index:
    """Página de bienvenida después de iniciar sesión."""

    def GET(self):
        # RNT01: valida la sesión antes de ejecutar
        if not AuthUsers().sesionValida():
            return render_login.login("Inicie sesión para continuar", "error")  # type: ignore

        return render.index()  # type: ignore
