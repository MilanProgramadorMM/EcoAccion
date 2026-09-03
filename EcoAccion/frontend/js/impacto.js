/* ==========================================================================
   impacto.js — Lógica de la pantalla "Mi impacto" (HU06)
   - Pide las estadísticas al backend (puntos + impacto ambiental)
   - Permite alternar entre "Este mes" y "Todo el tiempo"
   - Si el usuario no tiene acciones registradas, muestra un estado vacío
     en vez de números en cero sin contexto
   ========================================================================== */

const selectorPeriodo = document.getElementById("selector-periodo");
const panelImpacto = document.getElementById("panel-impacto");
const estadoVacio = document.getElementById("estado-vacio");

const valorPuntos = document.getElementById("valor-puntos");
const subtituloAcciones = document.getElementById("subtitulo-acciones");
const valorCo2 = document.getElementById("valor-co2");
const valorAgua = document.getElementById("valor-agua");
const valorEnergia = document.getElementById("valor-energia");
const valorArboles = document.getElementById("valor-arboles");

async function cargarEstadisticas(periodo = "mes") {
  try {
    const res = await fetch(`/api/estadisticas?periodo=${encodeURIComponent(periodo)}`);
    const data = await res.json();

    if (!data.ok) {
      mostrarEstadoVacio("No se pudieron cargar las estadísticas.");
      return;
    }

    // Sin acciones registradas -> estado vacío en vez de datos vacíos sin contexto
    if (data.total_acciones === 0) {
      mostrarEstadoVacio();
      return;
    }

    panelImpacto.hidden = false;
    estadoVacio.hidden = true;

    valorPuntos.textContent = data.total_puntos;
    subtituloAcciones.textContent =
      data.total_acciones === 1
        ? "1 acción registrada"
        : `${data.total_acciones} acciones registradas`;

    valorCo2.textContent = data.impacto.co2_evitado;
    valorAgua.textContent = data.impacto.agua_ahorrada;
    valorEnergia.textContent = data.impacto.energia_ahorrada;
    valorArboles.textContent = data.impacto.arboles_plantados;
  } catch (err) {
    mostrarEstadoVacio("No se pudo conectar con el servidor. Inténtalo de nuevo.");
  }
}

function mostrarEstadoVacio(mensaje) {
  panelImpacto.hidden = true;
  estadoVacio.hidden = false;
  estadoVacio.querySelector("p").textContent =
    mensaje || "Aún no has registrado acciones sostenibles en este período.";
}

selectorPeriodo.addEventListener("change", () => {
  cargarEstadisticas(selectorPeriodo.value);
});

// Carga inicial
cargarEstadisticas(selectorPeriodo.value);
