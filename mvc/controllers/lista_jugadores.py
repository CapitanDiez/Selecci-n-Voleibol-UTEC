import web
import logging
from typing import Any
from mvc.models.model_sesiones import ModelSesiones
from mvc.models.model_jugadores import ModelJugadores

logger = logging.getLogger(__name__)

render = web.template.render("mvc/views", base="template", globals={"web": web})


class ListaJugadores:
    """Lista de jugadores: RF-06, RF-09, RF-13 y botones de RF-12."""

    def GET(self):
        # RNT01: valida la sesión antes de ejecutar
        if not ModelSesiones().sesionValida():
            raise web.seeother("/login")

        # Filtros que llegan por la URL; si no vienen, usa estos valores
        filtros = web.input(rama="femenil", estado="todos", buscar="")

        lista: list[dict[str, Any]] = []
        datos: dict[str, int] = {"total": 0, "activos": 0, "activos_rama": 0, "promedio": 0, "posibles_bajas": 0}

        try:
            model_jugadores = ModelJugadores()
            jugadores = model_jugadores.obtenerJugadores()
            asistencias = model_jugadores.obtenerAsistencias()

            suma_porcentajes = 0
            datos["total"] = len(jugadores)

            for jugador in jugadores:
                # Asistencias de este jugador (de la más reciente a la más antigua)
                registros = []
                for asistencia in asistencias:
                    if asistencia["jugador_id"] == jugador["id"]:
                        registros.append(asistencia)

                # RF-06: porcentaje de asistencia (la falta justificada no cuenta como falta)
                asistio = 0
                for registro in registros:
                    if registro["estado"] != "falta":
                        asistio = asistio + 1
                porcentaje = 0
                if len(registros) > 0:
                    porcentaje = round(asistio * 100 / len(registros))
                jugador["porcentaje"] = porcentaje

                # RF-13: posible baja si no asistió a ninguno de sus últimos 12 entrenamientos
                ultimos = registros[:12]
                presente = False
                for registro in ultimos:
                    if registro["estado"] == "presente":
                        presente = True

                if jugador["estado"] == "baja":
                    jugador["situacion"] = "baja"
                elif len(ultimos) == 12 and not presente:
                    jugador["situacion"] = "posible baja"
                    datos["posibles_bajas"] = datos["posibles_bajas"] + 1
                else:
                    jugador["situacion"] = "activo"

                if jugador["estado"] == "activo":
                    datos["activos"] = datos["activos"] + 1
                    suma_porcentajes = suma_porcentajes + porcentaje
                    if jugador["rama"] == filtros.rama:
                        datos["activos_rama"] = datos["activos_rama"] + 1

                # RNT02: el id viaja firmado en la URL (id:HASH)
                jugador["id_hash"] = model_jugadores.generarHash(jugador["id"])

            if datos["activos"] > 0:
                datos["promedio"] = round(suma_porcentajes / datos["activos"])

            # RF-09: solo la rama seleccionada; filtro de estado y buscador
            texto = filtros.buscar.strip().lower()
            for jugador in jugadores:
                if jugador["rama"] != filtros.rama:
                    continue
                if filtros.estado == "activos" and jugador["situacion"] != "activo":
                    continue
                if filtros.estado == "posible_baja" and jugador["situacion"] != "posible baja":
                    continue
                if filtros.estado == "baja" and jugador["situacion"] != "baja":
                    continue
                if texto != "" and texto not in jugador["nombre"].lower() and texto not in jugador["matricula"]:
                    continue
                lista.append(jugador)
        except Exception as error:
            logger.error("ERROR 503: %s", error)
            print(f"ERROR 503: {str(error)}")

        return render.lista_jugadores(lista, datos, filtros)  # type: ignore
