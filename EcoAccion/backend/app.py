"""
app.py — Backend de EcoAccion (Flask).

Expone la API REST para dos historias de usuario:
  - HU03: registrar una acción sostenible  ->  POST /api/acciones
  - HU08: consultar el ranking             ->  GET  /api/ranking

Además sirve el frontend estático (carpeta ../frontend) para que todo
el proyecto se ejecute con un solo comando:  python app.py
"""
import os
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory

import db

# Ruta absoluta a la carpeta del frontend (../frontend respecto a este archivo)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=None)

# Inicializa la base de datos al arrancar (crea tablas + siembra si hace falta).
db.init_db()


# ---------------------------------------------------------------------------
#  Rutas que sirven el frontend
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    # Página de inicio -> formulario de registrar acción (HU03)
    return send_from_directory(FRONTEND_DIR, "registrar.html")


@app.route("/<path:archivo>")
def estaticos(archivo):
    # Sirve cualquier otro archivo del frontend (html, css, js)
    return send_from_directory(FRONTEND_DIR, archivo)


# ---------------------------------------------------------------------------
#  HU03 — Registrar acción sostenible
# ---------------------------------------------------------------------------
@app.route("/api/acciones", methods=["POST"])
def registrar_accion():
    """
    Registra una acción sostenible del usuario autenticado.

    Criterios de aceptación (Trello HU03):
      - Valida que categoría, descripción y fecha estén completos.
      - La acción queda asociada al perfil del usuario autenticado.
      - Responde con error claro si el registro falla.
    """
    datos = request.get_json(silent=True) or {}

    categoria = (datos.get("categoria") or "").strip()
    fecha = (datos.get("fecha") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()

    # --- Validación de campos obligatorios ---
    errores = {}
    if not categoria:
        errores["categoria"] = "Selecciona un tipo de acción."
    elif categoria not in db.CATEGORIAS:
        errores["categoria"] = "El tipo de acción no es válido."

    if not fecha:
        errores["fecha"] = "La fecha es obligatoria."
    else:
        # Verifica que la fecha tenga formato YYYY-MM-DD válido
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            errores["fecha"] = "La fecha no tiene un formato válido."

    if not descripcion:
        errores["descripcion"] = "La descripción es obligatoria."
    elif len(descripcion) > 200:
        errores["descripcion"] = "La descripción no puede superar los 200 caracteres."

    if errores:
        # 422 = entidad no procesable (fallo de validación)
        return jsonify({"ok": False, "errores": errores}), 422

    # --- Asociación al usuario autenticado ---
    usuario = db.get_usuario_actual()
    if usuario is None:
        return jsonify({"ok": False, "mensaje": "No hay un usuario autenticado."}), 401

    puntos = db.CATEGORIAS[categoria]["puntos"]
    ods = db.CATEGORIAS[categoria]["ods"]

    # --- Persistencia con manejo de errores ---
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO acciones (usuario_id, categoria, fecha, descripcion, puntos, ods)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (usuario["id"], categoria, fecha, descripcion, puntos, ods),
        )
        # Cada acción suma puntos al perfil -> alimenta el ranking (HU08)
        cur.execute(
            "UPDATE usuarios SET puntos = puntos + ? WHERE id = ?;",
            (puntos, usuario["id"]),
        )
        conn.commit()
        accion_id = cur.lastrowid
        conn.close()
    except Exception as exc:  # noqa: BLE001 - queremos notificar cualquier fallo
        # Notifica al usuario si el registro falla (criterio de aceptación)
        return jsonify({
            "ok": False,
            "mensaje": "No se pudo guardar la acción. Inténtalo de nuevo.",
            "detalle": str(exc),
        }), 500

    return jsonify({
        "ok": True,
        "mensaje": f"¡Acción registrada! Ganaste {puntos} puntos.",
        "accion": {
            "id": accion_id,
            "categoria": categoria,
            "fecha": fecha,
            "descripcion": descripcion,
            "puntos": puntos,
            "ods": ods,
            "usuario": usuario["nombre"],
        },
    }), 201


@app.route("/api/categorias", methods=["GET"])
def listar_categorias():
    """Devuelve las categorías disponibles para llenar el <select> del formulario."""
    categorias = [
        {"valor": clave, "puntos": info["puntos"], "ods": info["ods"]}
        for clave, info in db.CATEGORIAS.items()
    ]
    return jsonify({"ok": True, "categorias": categorias})


# ---------------------------------------------------------------------------
#  HU08 — Consultar ranking
# ---------------------------------------------------------------------------
@app.route("/api/ranking", methods=["GET"])
def obtener_ranking():
    """
    Devuelve los usuarios ordenados por puntos acumulados (mayor a menor).

    Criterios de aceptación (Trello HU08):
      - Obtiene y ordena a los usuarios por puntos (desc).
    Parámetro opcional ?tipo=amigos para filtrar solo amigos + el usuario actual.
    """
    tipo = (request.args.get("tipo") or "global").lower()

    conn = db.get_connection()
    if tipo == "amigos":
        # Muestra a los amigos y también al usuario actual, para poder compararse
        filas = conn.execute(
            """
            SELECT id, nombre, puntos, es_actual
            FROM usuarios
            WHERE es_amigo = 1 OR es_actual = 1
            ORDER BY puntos DESC, nombre ASC;
            """
        ).fetchall()
    else:
        filas = conn.execute(
            """
            SELECT id, nombre, puntos, es_actual
            FROM usuarios
            ORDER BY puntos DESC, nombre ASC;
            """
        ).fetchall()
    conn.close()

    ranking = []
    for posicion, fila in enumerate(filas, start=1):
        ranking.append({
            "posicion": posicion,
            "id": fila["id"],
            "nombre": fila["nombre"],
            "puntos": fila["puntos"],
            "es_actual": bool(fila["es_actual"]),
        })

    return jsonify({"ok": True, "tipo": tipo, "ranking": ranking})


if __name__ == "__main__":
    # debug=True recarga el servidor al guardar cambios (útil mientras desarrollas)
    app.run(host="127.0.0.1", port=5000, debug=True)
