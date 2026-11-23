import web
import logging
from typing import Any
from mvc.models.model_sesiones import ModelSesiones
from mvc.models.model_jugadores import ModelJugadores
from mvc.models.model_fotos import ModelFotos, FOTO_DEFAULT

logger = logging.getLogger(__name__)

render = web.template.render("mvc/views", base="template", globals={"web": web})

# Opciones de los <select> del formulario
CARRERAS: list[str] = [
    "TI e Innovación Digital",
    "Mecatrónica",
    "Contaduría",
    "Administración",
    "Turismo",
    "Mantenimiento Industrial",
    "Energías Renovables",
]

POSICIONES: list[tuple[str, str]] = [
    ("colocador", "Colocador(a)"),
    ("opuesto", "Opuesto(a)"),
    ("central", "Central"),
    ("receptor", "Receptor(a)"),
    ("libero", "Líbero"),
]

OBLIGATORIOS: list[str] = ["nombre", "matricula", "correo", "edad", "cuatrimestre", "carrera", "rama", "posicion", "numero_playera"]

# RF-20: solo el entrenador y el capitán registran jugadores
ROLES = ["entrenador", "capitan"]


class InsertarJugador:
    """Agregar jugador: RF-02 (validación) y RF-11 (guardar)."""

    def GET(self):
        # RNT01: valida la sesión antes de ejecutar
        model_sesiones = ModelSesiones()
        if not model_sesiones.sesionValida():
            raise web.seeother("/login")
        if not model_sesiones.tieneRol(ROLES):
            raise web.seeother("/lista_jugadores")

        return render.insertar_jugador({}, [], CARRERAS, POSICIONES)  # type: ignore

    def POST(self):
        model_sesiones = ModelSesiones()
        if not model_sesiones.sesionValida():
            raise web.seeother("/login")
        if not model_sesiones.tieneRol(ROLES):
            raise web.seeother("/lista_jugadores")

        # foto={} hace que web.py entregue el archivo completo
        formulario = web.input(foto={})
        datos: dict[str, Any] = {}
        for campo in OBLIGATORIOS + ["telefono"]:
            datos[campo] = str(formulario.get(campo, "")).strip()

        errores: list[str] = []

        try:
            model_jugadores = ModelJugadores()
            model_fotos = ModelFotos()

            # RF-02: todos los campos obligatorios completos
            for campo in OBLIGATORIOS:
                if datos[campo] == "":
                    errores.append("Completa todos los campos marcados con *.")
                    break

            if datos["matricula"] != "" and (not datos["matricula"].isdigit() or len(datos["matricula"]) != 10):
                errores.append("La matrícula debe tener 10 dígitos.")

            # RF-11: matrícula única y número de playera sin repetir en la rama
            if datos["matricula"] != "" and model_jugadores.existeMatricula(datos["matricula"]):
                errores.append(f"La matrícula {datos['matricula']} ya está registrada.")
            if datos["rama"] != "" and datos["numero_playera"].isdigit():
                if model_jugadores.existeNumero(datos["rama"], int(datos["numero_playera"])):
                    errores.append(f"El número {datos['numero_playera']} ya lo usa otro jugador de la rama {datos['rama']}.")

            # RTT04: la foto es opcional; si viene, se valida la extensión
            archivo = formulario.foto
            hay_foto = hasattr(archivo, "filename") and archivo.filename != ""
            if hay_foto and not model_fotos.extensionValida(archivo.filename):
                errores.append("La foto debe ser .jpg, .jpeg, .png o .webp.")

            if errores != []:
                return render.insertar_jugador(datos, errores, CARRERAS, POSICIONES)  # type: ignore

            # Guarda la foto en static/fotos/
            datos["foto"] = FOTO_DEFAULT
            if hay_foto:
                nombre_foto = model_fotos.guardarFoto(archivo)
                if nombre_foto is None:
                    errores.append("No se pudo guardar la foto.")
                    return render.insertar_jugador(datos, errores, CARRERAS, POSICIONES)  # type: ignore
                datos["foto"] = nombre_foto

            if datos["telefono"] == "":
                datos["telefono"] = None
            datos["edad"] = int(datos["edad"])
            datos["cuatrimestre"] = int(datos["cuatrimestre"])
            datos["numero_playera"] = int(datos["numero_playera"])

            # RF-11: guarda al jugador con estado activo
            jugador = model_jugadores.insertarJugador(datos)
            if jugador == []:
                # Si no se guardó, borra la foto para no dejar archivos sueltos
                model_fotos.borrarFoto(datos["foto"])
                errores.append("No se pudo guardar el jugador, intente de nuevo.")
                return render.insertar_jugador(datos, errores, CARRERAS, POSICIONES)  # type: ignore

            logger.info("Jugador registrado: %s", datos["matricula"])
            return render.jugador_insertado(jugador)  # type: ignore
        except Exception as error:
            logger.error("ERROR 504: %s", error)
            print(f"ERROR 504: {str(error)}")
            errores.append("Ocurrió un error, intente de nuevo.")
            return render.insertar_jugador(datos, errores, CARRERAS, POSICIONES)  # type: ignore
