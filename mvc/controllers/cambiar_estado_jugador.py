import web
import logging
from mvc.models.auth_users import AuthUsers
from mvc.models.model_jugadores import ModelJugadores

logger = logging.getLogger(__name__)

render_login = web.template.render("mvc/views")
render = web.template.render("mvc/views", base="template", globals={"web": web})

# RF-12 y RF-20: solo el entrenador da de baja o reactiva
ROLES = ["entrenador"]


class CambiarEstadoJugador:
    """RF-12: dar de baja o reactivar a un jugador sin borrar su historial."""

    def GET(self, id_hash: str):
        auth_users = AuthUsers()
        if not auth_users.sesionValida():
            return render_login.login("Inicie sesión para continuar", "error")  # type: ignore
        if not auth_users.tieneRol(ROLES):
            return render.sin_permiso()  # type: ignore

        try:
            # Si el HASH fue alterado, buscarJugador regresa []
            jugador = ModelJugadores().buscarJugador(id_hash)
        except Exception as error:
            logger.error("ERROR 505: %s", error)
            print(f"ERROR 505: {str(error)}")
            jugador = []

        return render.cambiar_estado_jugador(jugador, id_hash)  # type: ignore

    def POST(self, id_hash: str):
        auth_users = AuthUsers()
        if not auth_users.sesionValida():
            return render_login.login("Inicie sesión para continuar", "error")  # type: ignore
        if not auth_users.tieneRol(ROLES):
            return render.sin_permiso()  # type: ignore

        try:
            model_jugadores = ModelJugadores()

            # Valida de nuevo el id:HASH antes de cambiar nada
            jugador = model_jugadores.buscarJugador(id_hash)
            if jugador == []:
                return render.cambiar_estado_jugador([], id_hash)  # type: ignore

            if jugador[0]["estado"] == "activo":
                nuevo_estado = "baja"
            else:
                nuevo_estado = "activo"

            jugador = model_jugadores.cambiarEstado(id_hash, nuevo_estado)
            logger.info("Jugador %s cambió a %s", id_hash.split(":")[0], nuevo_estado)
            return render.estado_cambiado(jugador)  # type: ignore
        except Exception as error:
            logger.error("ERROR 506: %s", error)
            print(f"ERROR 506: {str(error)}")
            return render.cambiar_estado_jugador([], id_hash)  # type: ignore
