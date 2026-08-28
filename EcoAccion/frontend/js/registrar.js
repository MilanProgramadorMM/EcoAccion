/* ==========================================================================
   registrar.js — Lógica de la pantalla "Registrar acción" (HU03)
   - Carga las categorías desde el backend
   - Valida los campos obligatorios antes de enviar
   - Notifica éxito o error al usuario
   ========================================================================== */

const form = document.getElementById("form-accion");
const selectCategoria = document.getElementById("categoria");
const inputFecha = document.getElementById("fecha");
const textareaDescripcion = document.getElementById("descripcion");
const contador = document.getElementById("contador");
const aviso = document.getElementById("aviso");
const btnGuardar = document.getElementById("btn-guardar");

// Etiquetas legibles para cada categoría que devuelve el backend
const ETIQUETAS = {
  reciclaje: "Reciclaje",
  movilidad: "Movilidad sostenible",
  ahorro_energia: "Ahorro de energía",
  ahorro_agua: "Ahorro de agua",
  consumo_local: "Consumo local",
  reforestacion: "Reforestación",
};

// --- Cargar categorías al abrir la pantalla ---
async function cargarCategorias() {
  try {
    const res = await fetch("/api/categorias");
    const data = await res.json();
    data.categorias.forEach((cat) => {
      const opcion = document.createElement("option");
      opcion.value = cat.valor;
      const etiqueta = ETIQUETAS[cat.valor] || cat.valor;
      opcion.textContent = `${etiqueta} (+${cat.puntos} pts)`;
      selectCategoria.appendChild(opcion);
    });
  } catch (err) {
    mostrarAviso("No se pudieron cargar los tipos de acción.", false);
  }
}

// --- Contador de caracteres de la descripción ---
textareaDescripcion.addEventListener("input", () => {
  contador.textContent = textareaDescripcion.value.length;
});

// --- Utilidades de validación visual ---
function marcarError(campoId, mensaje) {
  document.getElementById(`campo-${campoId}`).classList.add("invalido");
  document.getElementById(`error-${campoId}`).textContent = mensaje;
}

function limpiarErrores() {
  ["categoria", "fecha", "descripcion"].forEach((id) => {
    document.getElementById(`campo-${id}`).classList.remove("invalido");
    document.getElementById(`error-${id}`).textContent = "";
  });
  aviso.className = "aviso";
  aviso.textContent = "";
}

function mostrarAviso(mensaje, exito) {
  aviso.textContent = mensaje;
  aviso.className = "aviso " + (exito ? "exito" : "fallo");
}

// Valida en el cliente antes de enviar (el backend vuelve a validar por seguridad)
function validarEnCliente() {
  let valido = true;

  if (!selectCategoria.value) {
    marcarError("categoria", "Selecciona un tipo de acción.");
    valido = false;
  }
  if (!inputFecha.value) {
    marcarError("fecha", "La fecha es obligatoria.");
    valido = false;
  }
  if (!textareaDescripcion.value.trim()) {
    marcarError("descripcion", "La descripción es obligatoria.");
    valido = false;
  }
  return valido;
}

// --- Envío del formulario ---
form.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  limpiarErrores();

  if (!validarEnCliente()) {
    mostrarAviso("Completa los campos obligatorios.", false);
    return;
  }

  const payload = {
    categoria: selectCategoria.value,
    fecha: inputFecha.value,
    descripcion: textareaDescripcion.value.trim(),
  };

  btnGuardar.disabled = true;
  btnGuardar.textContent = "Guardando...";

  try {
    const res = await fetch("/api/acciones", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (res.ok && data.ok) {
      mostrarAviso(data.mensaje, true);
      form.reset();
      contador.textContent = "0";
    } else if (data.errores) {
      // Errores de validación devueltos por el backend
      Object.entries(data.errores).forEach(([campo, msj]) => marcarError(campo, msj));
      mostrarAviso("Revisa los campos marcados.", false);
    } else {
      // Error del servidor -> notifica al usuario (criterio HU03)
      mostrarAviso(data.mensaje || "No se pudo registrar la acción.", false);
    }
  } catch (err) {
    // Fallo de red / servidor caído
    mostrarAviso("Error de conexión. Verifica tu red e inténtalo de nuevo.", false);
  } finally {
    btnGuardar.disabled = false;
    btnGuardar.textContent = "Guardar acción";
  }
});

// Inicialización
cargarCategorias();
