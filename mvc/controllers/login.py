import web
import logging
from mvc.models.auth_users import AuthUsers

logger = logging.getLogger(__name__)

# El login no usa template.html porque no lleva menú lateral
render_login = web.template.render("mvc/views")
render = web.template.render("mvc/views", base="template", globals={"web": web})


class Login:
    """RF-01: inicio de sesión con Supabase Authentication."""

    def GET(self):
        return render_login.login("", "")  # type: ignore

    def POST(self):
        formulario = web.input(email="", password="")
        email: str = formulario.email.strip()
        password: str = formulario.password

        try:
            auth_users = AuthUsers()

            # 1. Valida email y contraseña en Supabase Authentication
            token = auth_users.iniciarSesion(email, password)
            if token is None:
                return render_login.login("Credenciales incorrectas, verifique sus datos", "error")  # type: ignore

            # 2. Revisa que esté activo en la tabla usuarios y obtiene su rol
            usuario = auth_users.obtenerUsuario(email)
            if usuario == []:
                return render_login.login("Su usuario no tiene acceso al sistema", "error")  # type: ignore

            # 3. Registra el token en sesiones_abiertas y lo guarda en la sesión local
            auth_users.registrarToken(token)
            sesion = web.config.sesion
            sesion.token = token
            sesion.email = email
            sesion.nombre = usuario[0]["nombre"]
            sesion.rol = usuario[0]["rol"]
            logger.info("Inicio de sesión: %s (%s)", email, sesion.rol)
        except Exception as error:
            logger.error("ERROR 501: %s", error)
            print(f"ERROR 501: {str(error)}")
            return render_login.login("No se pudo iniciar sesión, intente de nuevo", "error")  # type: ignore

        # 4. Muestra la página de bienvenida
        return render.index()  # type: ignore
