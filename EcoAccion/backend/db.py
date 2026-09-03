"""
db.py — Capa de acceso a datos de EcoAccion (SQLite).

Crea la base de datos, define las tablas y siembra datos iniciales
que coinciden con el mockup del ranking. Mantener aquí toda la lógica
de base de datos hace que app.py se enfoque solo en las rutas/API.
"""
import os
import sqlite3
from datetime import datetime

# La base de datos vive junto a este archivo (backend/ecoaccion.db)
DB_PATH = os.path.join(os.path.dirname(__file__), "ecoaccion.db")

# Categorías de acción sostenible y los puntos que otorga cada una.
# Cada categoría se asocia a un ODS (Objetivo de Desarrollo Sostenible),
# lo cual conecta con la HU03 ("conocer mi progreso frente a los ODS").
# "impacto" son los valores estimados que aporta CADA acción de esa
# categoría y alimentan la HU06 ("visualizar impacto ambiental").
CATEGORIAS = {
    "reciclaje": {
        "puntos": 20, "ods": "ODS 12 - Producción y consumo responsables",
        "impacto": {"co2": 2, "agua": 0, "energia": 0, "arboles": 0},
    },
    "movilidad": {
        "puntos": 25, "ods": "ODS 11 - Ciudades y comunidades sostenibles",
        "impacto": {"co2": 3, "agua": 0, "energia": 0, "arboles": 0},
    },
    "ahorro_energia": {
        "puntos": 15, "ods": "ODS 7 - Energía asequible y no contaminante",
        "impacto": {"co2": 1, "agua": 0, "energia": 5, "arboles": 0},
    },
    "ahorro_agua": {
        "puntos": 15, "ods": "ODS 6 - Agua limpia y saneamiento",
        "impacto": {"co2": 0, "agua": 40, "energia": 0, "arboles": 0},
    },
    "consumo_local": {
        "puntos": 10, "ods": "ODS 12 - Producción y consumo responsables",
        "impacto": {"co2": 1, "agua": 0, "energia": 0, "arboles": 0},
    },
    "reforestacion": {
        "puntos": 30, "ods": "ODS 15 - Vida de ecosistemas terrestres",
        "impacto": {"co2": 5, "agua": 0, "energia": 0, "arboles": 1},
    },
}


def get_connection():
    """Devuelve una conexión con filas accesibles por nombre de columna."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Habilita las llaves foráneas (SQLite las ignora por defecto)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Crea las tablas si no existen y siembra datos de ejemplo una sola vez."""
    conn = get_connection()
    cur = conn.cursor()

    # Tabla de usuarios (perfil). 'es_actual' marca al usuario "logueado"
    # de demostración: en un sistema real vendría de la sesión/autenticación.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT    NOT NULL,
            puntos    INTEGER NOT NULL DEFAULT 0,
            es_amigo  INTEGER NOT NULL DEFAULT 0,  -- 1 = amigo del usuario actual
            es_actual INTEGER NOT NULL DEFAULT 0   -- 1 = usuario autenticado (demo)
        );
        """
    )

    # Tabla de acciones sostenibles registradas (HU03).
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS acciones (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER NOT NULL,
            categoria   TEXT    NOT NULL,
            fecha       TEXT    NOT NULL,
            descripcion TEXT    NOT NULL,
            puntos      INTEGER NOT NULL DEFAULT 0,
            ods         TEXT,
            creada_en   TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        );
        """
    )

    # Siembra solo si la tabla está vacía, para no duplicar en cada arranque.
    cur.execute("SELECT COUNT(*) AS n FROM usuarios;")
    if cur.fetchone()["n"] == 0:
        usuarios_demo = [
            # (nombre,      puntos, es_amigo, es_actual)
            ("María G.",    500, 1, 0),
            ("Juan P.",     480, 0, 0),
            ("Ana L.",      450, 1, 0),
            ("Carlos M.",   380, 0, 0),
            ("Tú",          350, 0, 1),   # usuario autenticado de demostración
        ]
        cur.executemany(
            "INSERT INTO usuarios (nombre, puntos, es_amigo, es_actual) VALUES (?, ?, ?, ?);",
            usuarios_demo,
        )

    conn.commit()
    conn.close()


def get_usuario_actual():
    """Devuelve el usuario autenticado de demostración (fila con es_actual = 1)."""
    conn = get_connection()
    fila = conn.execute("SELECT * FROM usuarios WHERE es_actual = 1 LIMIT 1;").fetchone()
    conn.close()
    return fila


def get_estadisticas(usuario_id, periodo="mes"):
    """
    Calcula el resumen de impacto ambiental de un usuario (HU06).

    - periodo="mes":  solo acciones registradas desde el día 1 del mes actual.
    - periodo="todo": historial completo del usuario.

    Los indicadores (CO2 evitado, agua ahorrada, energía ahorrada, árboles
    plantados) se derivan de la categoría de cada acción registrada, así que
    se recalculan siempre que el usuario registra una acción nueva.
    """
    conn = get_connection()
    if periodo == "mes":
        desde = datetime.now().strftime("%Y-%m-01")
        filas = conn.execute(
            """
            SELECT categoria, COUNT(*) AS cantidad, SUM(puntos) AS puntos
            FROM acciones
            WHERE usuario_id = ? AND fecha >= ?
            GROUP BY categoria;
            """,
            (usuario_id, desde),
        ).fetchall()
    else:
        filas = conn.execute(
            """
            SELECT categoria, COUNT(*) AS cantidad, SUM(puntos) AS puntos
            FROM acciones
            WHERE usuario_id = ?
            GROUP BY categoria;
            """,
            (usuario_id,),
        ).fetchall()
    conn.close()

    total_acciones = 0
    total_puntos = 0
    co2 = agua = energia = arboles = 0

    for fila in filas:
        cantidad = fila["cantidad"]
        total_acciones += cantidad
        total_puntos += fila["puntos"] or 0

        impacto = CATEGORIAS.get(fila["categoria"], {}).get("impacto", {})
        co2 += impacto.get("co2", 0) * cantidad
        agua += impacto.get("agua", 0) * cantidad
        energia += impacto.get("energia", 0) * cantidad
        arboles += impacto.get("arboles", 0) * cantidad

    return {
        "total_acciones": total_acciones,
        "total_puntos": total_puntos,
        "impacto": {
            "co2_evitado": co2,
            "agua_ahorrada": agua,
            "energia_ahorrada": energia,
            "arboles_plantados": arboles,
        },
    }


if __name__ == "__main__":
    # Permite inicializar la base de datos manualmente:  python db.py
    init_db()
    print(f"Base de datos lista en: {DB_PATH}")
