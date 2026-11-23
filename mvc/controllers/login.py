import web
import logging
from mvc.models.model_sesiones import ModelSesiones

logger = logging.getLogger(__name__)

# El login no usa template.html porque no lleva menú lateral
render = web.template.render("mvc/views")


class Login:
    """RF-01: inicio de sesión con Supabase Authentication."""

    def GET(self):
        return render.login("")  # type: ignore

    def POST(self):
        formulario = web.input(email="", password="")
        email: str = formulario.email.strip()
        password: str = formulario.password

        try:
            model_sesiones = ModelSesiones()

            # 1. Valida email y contraseña en Supabase Authentication
            token = model_sesiones.iniciarSesion(email, password)
            if token is None:
                return render.login("Credenciales incorrectas, verifique sus datos")  # type: ignore

            # 2. Revisa que esté activo en la tabla usuarios y obtiene su rol
            usuario = model_sesiones.obtenerUsuario(email)
            if usuario == []:
                return render.login("Su usuario no tiene acceso al sistema")  # type: ignore

            # 3. Registra el token en sesiones_abiertas y lo guarda en la sesión local
            model_sesiones.registrarToken(token)
            sesion = web.config.sesion
            sesion.token = token
            sesion.email = email
            sesion.nombre = usuario[0]["nombre"]
            sesion.rol = usuario[0]["rol"]
            logger.info("Inicio de sesión: %s (%s)", email, sesion.rol)
        except Exception as error:
            logger.error("ERROR 501: %s", error)
            print(f"ERROR 501: {str(error)}")
            return render.login("No se pudo iniciar sesión, intente de nuevo")  # type: ignore

        # 4. Redirige a la página de bienvenida
        raise web.seeother("/")
