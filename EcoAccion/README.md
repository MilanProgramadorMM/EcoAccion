# EcoAccion 🌱

Aplicación para registrar acciones sostenibles y motivar la participación mediante un ranking.

Este módulo cubre dos historias de usuario:

- **HU03 — Registrar acción sostenible:** formulario con validación de campos obligatorios (tipo, fecha, descripción), asociado al usuario autenticado, con aviso de éxito/error.
- **HU08 — Consultar ranking:** lista de participantes ordenada por puntos acumulados (mayor a menor), con pestañas *Global* / *Amigos* y resaltado del usuario actual.

Cada acción registrada suma puntos al perfil, y esos puntos se reflejan en el ranking, conectando ambas historias.

## Tecnologías

- **Frontend:** HTML, CSS y JavaScript (sin frameworks).
- **Backend:** Python + [Flask](https://flask.palletsprojects.com/).
- **Base de datos:** SQLite (se crea sola al ejecutar).

## Estructura

```
EcoAccion/
├── backend/
│   ├── app.py            # Servidor Flask + API (HU03 y HU08)
│   ├── db.py             # Base de datos SQLite y datos de ejemplo
│   └── requirements.txt  # Dependencias de Python
├── frontend/
│   ├── registrar.html    # Pantalla Registrar acción (HU03)
│   ├── ranking.html      # Pantalla Ranking (HU08)
│   ├── css/estilos.css
│   └── js/
│       ├── registrar.js
│       └── ranking.js
└── README.md
```

## Cómo ejecutar

Desde **Git Bash** (o cualquier terminal), en la carpeta del proyecto:

```bash
# 1. Instalar dependencias
pip install -r backend/requirements.txt

# 2. Levantar el servidor
cd backend
python app.py
```

Luego abre en el navegador: **http://127.0.0.1:5000**

- `/` → Registrar acción (HU03)
- `/ranking.html` → Ranking (HU08)

> La primera vez se crea el archivo `backend/ecoaccion.db` con 5 usuarios de ejemplo (los del mockup). No se sube al repositorio (está en `.gitignore`).

## API

| Método | Ruta               | Descripción                                        |
|--------|--------------------|----------------------------------------------------|
| GET    | `/api/categorias`  | Tipos de acción disponibles y sus puntos.          |
| POST   | `/api/acciones`    | Registra una acción. Valida campos obligatorios.   |
| GET    | `/api/ranking`     | Ranking global ordenado por puntos (desc).         |
| GET    | `/api/ranking?tipo=amigos` | Ranking solo de amigos + usuario actual.   |

### Ejemplo — registrar acción

```bash
curl -X POST http://127.0.0.1:5000/api/acciones \
  -H "Content-Type: application/json" \
  -d '{"categoria":"reciclaje","fecha":"2026-08-27","descripcion":"Separé residuos"}'
```

## Nota sobre autenticación

Para esta entrega, el "usuario autenticado" se simula con la fila marcada como
`es_actual = 1` en la tabla `usuarios` (el usuario **"Tú"**). Cuando el equipo
integre el login real, basta con reemplazar `db.get_usuario_actual()` por el
usuario de la sesión.
