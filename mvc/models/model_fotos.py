import os
import time
import logging

# Configura el sistema de logging
logger = logging.getLogger(__name__)

CARPETA_FOTOS = "static/fotos/"
EXTENSIONES = [".jpg", ".jpeg", ".png", ".webp"]
FOTO_DEFAULT = "default.png"


class ModelFotos:
    """RTT04: guarda y borra las fotos de los jugadores en static/fotos/."""

    def extensionValida(self, nombre_archivo: str) -> bool:
        """Solo acepta .jpg, .jpeg, .png y .webp."""
        try:
            extension = os.path.splitext(nombre_archivo)[1].lower()
            return extension in EXTENSIONES
        except Exception as error:
            logger.error("ERROR 301: %s", error)
            print(f"ERROR 301: {str(error)}")
            return False

    def guardarFoto(self, archivo) -> str | None:
        """
        Guarda la imagen con un timestamp al inicio para evitar nombres repetidos.
        Regresa el nombre con el que se guardó, o None si falla.
        """
        try:
            nombre_original = os.path.basename(archivo.filename)
            nombre = f"{int(time.time())}_{nombre_original.replace(' ', '_')}"
            with open(CARPETA_FOTOS + nombre, "wb") as destino:
                destino.write(archivo.file.read())
            return nombre
        except Exception as error:
            logger.error("ERROR 302: %s", error)
            print(f"ERROR 302: {str(error)}")
            return None

    def borrarFoto(self, nombre: str) -> bool:
        """Borra el archivo si existe y no es la imagen por defecto."""
        try:
            ruta = CARPETA_FOTOS + nombre
            if nombre != FOTO_DEFAULT and os.path.exists(ruta):
                os.remove(ruta)
            return True
        except Exception as error:
            logger.error("ERROR 303: %s", error)
            print(f"ERROR 303: {str(error)}")
            return False
