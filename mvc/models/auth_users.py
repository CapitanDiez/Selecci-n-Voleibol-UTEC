import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Any
import web
import logging

# Lee las variables de entorno
load_dotenv()

# Configura el sistema de logging
logger = logging.getLogger(__name__)


class AuthUsers:
    """Autenticación (RF-01), roles (RF-20) y validación de sesiones (RNT01).
    Basado en mvc/models/auth_users.py del repositorio del profesor."""

    def __init__(self) -> None:
        try:
            self.supabase: Client = create_client(
                os.environ.get("SUPABASE_URL", ""),
                os.environ.get("SUPABASE_KEY", "")
            )
        except Exception as error:
            logger.error("ERROR 100: %s", error)
            print(f"ERROR 100: {str(error)}")

    def iniciarSesion(self, email: str, password: str) -> str | None:
        """Valida las credenciales con Supabase Authentication y regresa el token JWT."""
        try:
            response = self.supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password
                }
            )
            return response.session.access_token  # type: ignore
        except Exception as error:
            logger.error("ERROR 101: %s", error)
            print(f"ERROR 101: {str(error)}")
            return None

    def registrarUsuario(self, email: str, password: str) -> str | None:
        try:
            response = self.supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password
                }
            )
            return response.user.id  # type: ignore
        except Exception as error:
            logger.error("ERROR 102: %s", error)
            print(f"ERROR 102: {str(error)}")
            return None

    def obtenerUsuario(self, email: str) -> list[dict[str, Any]]:
        """RF-01: solo entra si el usuario está activo y tiene un rol permitido."""
        try:
            # SELECT * FROM usuarios WHERE email = ? AND activo = true;
            response = self.supabase.table("usuarios").select("*").eq("email", email).eq("activo", True).execute()
            return response.data  # type: ignore
        except Exception as error:
            logger.error("ERROR 103: %s", error)
            print(f"ERROR 103: {str(error)}")
            return []

    def registrarToken(self, token: str) -> bool:
        """Guarda el token en la tabla sesiones_abiertas."""
        try:
            # INSERT INTO sesiones_abiertas(token) VALUES(?);
            self.supabase.table("sesiones_abiertas").insert({"token": token}).execute()
            return True
        except Exception as error:
            logger.error("ERROR 104: %s", error)
            print(f"ERROR 104: {str(error)}")
            return False

    def validarToken(self, token: str) -> bool:
        """Revisa que el token siga registrado en sesiones_abiertas."""
        try:
            # SELECT * FROM sesiones_abiertas WHERE token = ?;
            response = self.supabase.table("sesiones_abiertas").select("*").eq("token", token).execute()
            return response.data != []
        except Exception as error:
            logger.error("ERROR 105: %s", error)
            print(f"ERROR 105: {str(error)}")
            return False

    def eliminarToken(self, token: str) -> bool:
        """RF-02 (cerrar sesión): borra el token de sesiones_abiertas."""
        try:
            # DELETE FROM sesiones_abiertas WHERE token = ?;
            self.supabase.table("sesiones_abiertas").delete().eq("token", token).execute()
            return True
        except Exception as error:
            logger.error("ERROR 106: %s", error)
            print(f"ERROR 106: {str(error)}")
            return False

    def sesionValida(self) -> bool:
        """
        RNT01: se llama al inicio de CADA controlador privado.
        Revisa que exista sesión local y que el token siga en sesiones_abiertas.
        """
        try:
            token = web.config.sesion.get("token", "")
            if token == "":
                return False
            return self.validarToken(token)
        except Exception as error:
            logger.error("ERROR 107: %s", error)
            print(f"ERROR 107: {str(error)}")
            return False

    def tieneRol(self, roles: list[str]) -> bool:
        """RF-20: revisa que el usuario de la sesión tenga uno de los roles permitidos."""
        try:
            return web.config.sesion.get("rol", "") in roles
        except Exception as error:
            logger.error("ERROR 108: %s", error)
            print(f"ERROR 108: {str(error)}")
            return False


if __name__ == "__main__":
    objeto = AuthUsers()
    print(objeto.iniciarSesion("felix@utectulancingo.edu.mx", "cambiar123"))
