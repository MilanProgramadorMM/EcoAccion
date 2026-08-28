/* ==========================================================================
   ranking.js — Lógica de la pantalla "Ranking" (HU08)
   - Pide el ranking al backend (ordenado por puntos, mayor a menor)
   - Alterna entre Global y Amigos
   - Resalta al usuario actual ("Tú") y pone medallas al top 3
   ========================================================================== */

const lista = document.getElementById("lista-ranking");
const botonesPestana = document.querySelectorAll(".pestanas button");

const MEDALLAS = { 1: "🥇", 2: "🥈", 3: "🥉" };

// Iniciales para el avatar: "María G." -> "MG", "Tú" -> "TÚ"
function iniciales(nombre) {
  const partes = nombre.trim().split(/\s+/);
  if (partes.length === 1) return partes[0].slice(0, 2).toUpperCase();
  return (partes[0][0] + partes[1][0]).toUpperCase();
}

async function cargarRanking(tipo = "global") {
  lista.innerHTML = '<li class="cargando">Cargando ranking...</li>';
  try {
    const res = await fetch(`/api/ranking?tipo=${encodeURIComponent(tipo)}`);
    const data = await res.json();

    if (!data.ok || data.ranking.length === 0) {
      lista.innerHTML = '<li class="cargando">Aún no hay participantes.</li>';
      return;
    }

    lista.innerHTML = "";
    data.ranking.forEach((u) => {
      const li = document.createElement("li");
      li.className = "fila-ranking" + (u.es_actual ? " yo" : "");

      const medalla = MEDALLAS[u.posicion] || "";
      const marcaPosicion = medalla
        ? `<span class="medalla">${medalla}</span>`
        : `<span class="posicion">${u.posicion}</span>`;

      li.innerHTML = `
        ${marcaPosicion}
        <span class="avatar">${iniciales(u.nombre)}</span>
        <span class="nombre">${u.nombre}</span>
        <span class="puntos">${u.puntos} <span>pts</span></span>
      `;
      lista.appendChild(li);
    });
  } catch (err) {
    lista.innerHTML = '<li class="cargando">No se pudo cargar el ranking.</li>';
  }
}

// Cambio de pestaña Global / Amigos
botonesPestana.forEach((btn) => {
  btn.addEventListener("click", () => {
    botonesPestana.forEach((b) => b.classList.remove("activa"));
    btn.classList.add("activa");
    cargarRanking(btn.dataset.tipo);
  });
});

// Carga inicial
cargarRanking("global");
