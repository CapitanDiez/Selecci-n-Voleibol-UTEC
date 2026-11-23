# Gestor de la Selección de Voleibol · UTEC Tulancingo

Módulo **Acceso y gestión de jugadores** (`app.py`): RF-01, RF-02, RF-11, RF-12, RF-20,
más RF-06, RF-09 y RF-13 en la pantalla de Lista de jugadores.

Sigue la especificación del profe: MVC con controladores de acción única, Supabase Auth,
sesiones validadas contra `sesiones_abiertas`, IDs firmados con HMAC-SHA256 en la URL,
tipado, `try/except` con errores numerados, `logging` y fotos en `static/fotos/`.

## 1. Base de datos

1. Si aún no existen, crea las tablas del equipo (script `gestor_voleibol.sql`).
2. Ejecuta **`sql/ajustes_voleibol.sql`** en Supabase > SQL Editor (una sola vez). Hace esto:
   - Agrega `email` a `usuarios` y quita `contrasena` (la contraseña ahora la guarda Supabase Auth).
   - Crea la tabla `sesiones_abiertas`.
   - Agrega `foto` a `jugadores`.
3. En Supabase > **Authentication > Users > Add user**, crea los 3 usuarios con **los mismos emails**
   que pusiste en la tabla `usuarios` y márcalos como confirmados (*Auto Confirm User*).

## 2. Ejecutar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Crea un `.env` con `SUPABASE_URL` y `SUPABASE_KEY`.

## 3. Rutas

| Ruta | Controlador | Quién entra |
|---|---|---|
| `/login` | `login.py` | Todos |
| `/cerrar_sesion` | `cerrar_sesion.py` | Todos |
| `/` | `index.py` | Con sesión |
| `/lista_jugadores` | `lista_jugadores.py` | Entrenador, capitán, coordinación |
| `/insertar_jugador` | `insertar_jugador.py` | Entrenador, capitán |
| `/cambiar_estado_jugador/id:HASH` | `cambiar_estado_jugador.py` | Entrenador |

## 4. Para el resto del equipo

Cada controlador privado debe empezar así (RNT01 y RF-20):

```python
from mvc.models.model_sesiones import ModelSesiones

def GET(self):
    model_sesiones = ModelSesiones()
    if not model_sesiones.sesionValida():
        raise web.seeother("/login")
    if not model_sesiones.tieneRol(["entrenador"]):   # roles que pueden entrar
        raise web.seeother("/")
```

Y crear su `render` así, para que el menú y el usuario de `template.html` funcionen:

```python
render = web.template.render("mvc/views", base="template", globals={"web": web})
```

Para firmar ids en la URL, usar `generarHash` / `validarHash` (como en `model_jugadores.py`).

Rangos de errores: `1xx` sesiones · `2xx` jugadores · `3xx` fotos · `5xx` controladores.
