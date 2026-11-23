import os
from supabase import create_client, Client
from dotenv import load_dotenv
import hashlib
import hmac
from typing import Any, cast
import logging

# Lee las variables de entorno
load_dotenv()

# Configura el sistema de logging
logger = logging.getLogger(__name__)

# Clave para firmar los id en la URL (RTT05). Nota: no es la mejor opción tenerla aquí
CLAVE_SECRETA = b"voleibol_utec"


class ModelJugadores:
    """Gestión de jugadores (RF-02, RF-11, RF-12) y asistencias (RF-06, RF-13)."""

    def __init__(self) -> None:
        try:
            self.supabase: Client = create_client(
                os.environ.get("SUPABASE_URL", ""),
                os.environ.get("SUPABASE_KEY", "")
            )
        except Exception as error:
            logger.error("ERROR 200: %s", error)
            print(f"ERROR 200: {str(error)}")

    def generarHash(self, id: int) -> str:
        """RNT02: regresa 'id:firma' con HMAC-SHA256."""
        try:
            mensaje = str(id).encode("utf-8")
            firma = hmac.new(CLAVE_SECRETA, mensaje, hashlib.sha256).hexdigest()
            return f"{id}:{firma}"
        except Exception as error:
            logger.error("ERROR 201: %s", error)
            print(f"ERROR 201: {str(error)}")
            return ""

    def validarHash(self, hash_a_validar: str) -> int | None:
        """RNT02: si la firma es correcta regresa el id; si fue alterada regresa None."""
        try:
            id_str, sep, _ = hash_a_validar.partition(":")
            if sep and id_str.isdigit():
                esperado = self.generarHash(int(id_str))
                if hmac.compare_digest(esperado, hash_a_validar):
                    return int(id_str)
            return None
        except Exception as error:
            logger.error("ERROR 202: %s", error)
            print(f"ERROR 202: {str(error)}")
            return None

    def obtenerJugadores(self) -> list[dict[str, Any]]:
        try:
            # SELECT * FROM jugadores ORDER BY nombre;
            response = self.supabase.table("jugadores").select("*").order("nombre").execute()
            return cast(list[dict[str, Any]], response.data or [])
        except Exception as error:
            logger.error("ERROR 203: %s", error)
            print(f"ERROR 203: {str(error)}")
            return []

    def buscarJugador(self, id_hash: str) -> list[dict[str, Any]]:
        """Busca por 'id:HASH'. Si la firma no es válida regresa lista vacía."""
        try:
            id = self.validarHash(id_hash)
            if id is None:
                return []
            # SELECT * FROM jugadores WHERE id = ?;
            response = self.supabase.table("jugadores").select("*").eq("id", id).execute()
            return cast(list[dict[str, Any]], response.data or [])
        except Exception as error:
            logger.error("ERROR 204: %s", error)
            print(f"ERROR 204: {str(error)}")
            return []

    def existeMatricula(self, matricula: str) -> bool:
        """RF-11: la matrícula no puede estar registrada."""
        try:
            # SELECT id FROM jugadores WHERE matricula = ?;
            response = self.supabase.table("jugadores").select("id").eq("matricula", matricula).execute()
            return response.data != []
        except Exception as error:
            logger.error("ERROR 205: %s", error)
            print(f"ERROR 205: {str(error)}")
            return False

    def existeNumero(self, rama: str, numero_playera: int) -> bool:
        """RF-11: el número de playera no se repite dentro de la misma rama."""
        try:
            # SELECT id FROM jugadores WHERE rama = ? AND numero_playera = ?;
            response = self.supabase.table("jugadores").select("id").eq("rama", rama).eq("numero_playera", numero_playera).execute()
            return response.data != []
        except Exception as error:
            logger.error("ERROR 206: %s", error)
            print(f"ERROR 206: {str(error)}")
            return False

    def insertarJugador(self, datos: dict[str, Any]) -> list[dict[str, Any]]:
        """RF-11: guarda al jugador con estado 'activo'."""
        try:
            datos["estado"] = "activo"
            # INSERT INTO jugadores(...) VALUES(...);
            response = self.supabase.table("jugadores").insert(datos).execute()
            return cast(list[dict[str, Any]], response.data or [])
        except Exception as error:
            logger.error("ERROR 207: %s", error)
            print(f"ERROR 207: {str(error)}")
            return []

    def cambiarEstado(self, id_hash: str, estado: str) -> list[dict[str, Any]]:
        """RF-12: cambia a 'baja' o 'activo' sin borrar el registro ni su historial."""
        try:
            id = self.validarHash(id_hash)
            if id is None:
                return []
            # UPDATE jugadores SET estado = ? WHERE id = ?;
            response = self.supabase.table("jugadores").update({"estado": estado}).eq("id", id).execute()
            return cast(list[dict[str, Any]], response.data or [])
        except Exception as error:
            logger.error("ERROR 208: %s", error)
            print(f"ERROR 208: {str(error)}")
            return []

    def obtenerAsistencias(self) -> list[dict[str, Any]]:
        """Asistencias de todos los jugadores, de la más reciente a la más antigua."""
        try:
            # SELECT * FROM asistencias ORDER BY entrenamiento_id DESC;
            response = self.supabase.table("asistencias").select("*").order("entrenamiento_id", desc=True).execute()
            return cast(list[dict[str, Any]], response.data or [])
        except Exception as error:
            logger.error("ERROR 209: %s", error)
            print(f"ERROR 209: {str(error)}")
            return []


if __name__ == "__main__":
    model_jugadores = ModelJugadores()
    print(model_jugadores.obtenerJugadores())
    firma = model_jugadores.generarHash(1)
    print(firma, model_jugadores.validarHash(firma), model_jugadores.validarHash("1:alterado"))
