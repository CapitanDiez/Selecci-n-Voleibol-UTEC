import web
import logging
from mvc.models.auth_users import AuthUsers

logger = logging.getLogger(__name__)

render_login = web.template.render("mvc/views")


class CerrarSesion:
    """RF-02: cierra la sesión de forma segura."""

    def GET(self):
        try:
            sesion = web.config.sesion
            token: str = sesion.get("token", "")

            # 1. Elimina el token de sesiones_abiertas
            if token != "":
                AuthUsers().eliminarToken(token)
                logger.info("Cierre de sesión: %s", sesion.get("email", ""))

            # 2. Destruye la sesión local
            sesion.kill()
        except Exception as error:
            logger.error("ERROR 502: %s", error)
            print(f"ERROR 502: {str(error)}")

        # 3. Muestra el login
        return render_login.login("Sesión cerrada correctamente", "aviso")  # type: ignore
