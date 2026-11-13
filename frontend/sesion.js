// =====================================================================
// Utilidades compartidas por todas las páginas:
// sesión, llamadas a la API, escapado de HTML y formato de préstamos.
// Se debe cargar ANTES que app.js / portal.js.
// =====================================================================

const API_URL = 'http://localhost:8000';
const SESSION_KEY = 'usuario';
const ROLES_PERSONAL = ['BIBLIOTECARIO', 'ADMINISTRADOR'];
// Carpeta frontend/, para armar rutas sin importar en qué subcarpeta esté la página
const APP_BASE = new URL('.', document.currentScript.src);

// ---------------------------------------------------------------------
// SESIÓN (se guarda en sessionStorage al iniciar sesión en Login/)
// ---------------------------------------------------------------------
function obtenerSesion() {
    try {
        return JSON.parse(sessionStorage.getItem(SESSION_KEY));
    } catch (e) {
        return null;
    }
}

function guardarSesion(datos) {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(datos));
}

function irA(ruta) {
    window.location.replace(new URL(ruta, APP_BASE));
}

function esPersonal(sesion) {
    return Boolean(sesion && ROLES_PERSONAL.includes(sesion.rol));
}

// Página principal según el tipo de cuenta
function paginaInicio(sesion) {
    return esPersonal(sesion) ? 'index.html' : 'portal/index.html';
}

function cerrarSesion() {
    sessionStorage.removeItem(SESSION_KEY);
    irA('Login/index.html');
}

// Corta la carga de la página si no hay sesión o si el rol no corresponde.
// tipo: 'personal' (bibliotecario/administrador) o 'cliente'.
function requerirSesion(tipo) {
    const sesion = obtenerSesion();
    if (!sesion || !sesion.token) {
        irA('Login/index.html');
        return null;
    }
    const permitido = tipo === 'personal' ? esPersonal(sesion) : sesion.rol === 'CLIENTE';
    if (!permitido) {
        irA(paginaInicio(sesion));
        return null;
    }
    return sesion;
}

// Agrega al menú lateral el nombre de quien inició sesión y el botón de salir
function mostrarUsuarioEnMenu(sesion) {
    const menu = document.querySelector('.sidebar-menu');
    if (!sesion || !menu) return;

    const seccion = document.createElement('div');
    seccion.className = 'menu-section';

    const titulo = document.createElement('p');
    titulo.className = 'section-title';
    titulo.textContent = `${sesion.nombre} · ${sesion.cargo}`;

    const salir = document.createElement('a');
    salir.href = '#';
    salir.className = 'menu-item';
    salir.textContent = 'Cerrar sesión';
    salir.addEventListener('click', (e) => {
        e.preventDefault();
        cerrarSesion();
    });

    seccion.append(titulo, salir);
    menu.append(seccion);
}

// ---------------------------------------------------------------------
// LLAMADAS A LA API
// ---------------------------------------------------------------------

// Convierte la respuesta de error de FastAPI en un mensaje legible
function mensajeDeError(datos, status) {
    const detalle = datos && datos.detail;
    if (typeof detalle === 'string') return detalle;
    if (Array.isArray(detalle)) {
        // Errores de validación (422): [{loc: ['body', 'campo'], msg: '...'}]
        return 'Revisa los datos:\n' + detalle
            .map(e => `• ${(e.loc || []).slice(1).join(' ')}: ${e.msg}`)
            .join('\n');
    }
    return `Error ${status}`;
}

// fetch con el token de sesión. Lanza Error con el mensaje del backend si algo falla.
async function api(endpoint, { method = 'GET', body } = {}) {
    const sesion = obtenerSesion();
    const headers = {};
    if (sesion && sesion.token) headers.Authorization = `Bearer ${sesion.token}`;
    if (body !== undefined) headers['Content-Type'] = 'application/json';

    let res;
    try {
        res = await fetch(`${API_URL}${endpoint}`, {
            method,
            headers,
            body: body !== undefined ? JSON.stringify(body) : undefined,
        });
    } catch (e) {
        throw new Error('No se pudo conectar con el servidor. ¿Está corriendo el backend?');
    }

    if (res.status === 401) {
        cerrarSesion();
        throw new Error('Tu sesión expiró. Vuelve a iniciar sesión.');
    }
    const datos = await res.json().catch(() => null);
    if (!res.ok) throw new Error(mensajeDeError(datos, res.status));
    return datos;
}

// ---------------------------------------------------------------------
// HTML SEGURO
// ---------------------------------------------------------------------

// Escapa texto antes de meterlo en innerHTML. Sin esto, un título como
// "O'Brien" rompía los botones y un texto con <script> se ejecutaba.
function esc(valor) {
    return String(valor ?? '').replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
}

// Llena un <select> con opciones [{value, text}]
function llenarSelect(select, opciones, textoVacio) {
    select.innerHTML = textoVacio ? `<option value="">${esc(textoVacio)}</option>` : '';
    opciones.forEach(o => {
        select.insertAdjacentHTML('beforeend',
            `<option value="${esc(o.value)}">${esc(o.text)}</option>`);
    });
}

// Un solo listener por tabla para los botones de cada fila (data-accion / data-id)
function delegarAcciones(tbody, acciones) {
    tbody.addEventListener('click', (e) => {
        const boton = e.target.closest('button[data-accion]');
        if (boton && acciones[boton.dataset.accion]) {
            acciones[boton.dataset.accion](boton.dataset.id);
        }
    });
}

// ---------------------------------------------------------------------
// FORMATO DE PRÉSTAMOS
// ---------------------------------------------------------------------
function formatoFecha(iso) {
    if (!iso) return '—';
    const [anio, mes, dia] = iso.split('-');
    return `${dia}/${mes}/${anio}`;
}

function claseEstado(estado) {
    return {
        VENCIDO: 'red', DEVUELTO: 'green', APARTADO: 'amber', ACTIVO: 'blue',
    }[estado] || 'gray';
}

function plural(n, palabra) {
    return `${n} ${palabra}${n === 1 ? '' : 's'}`;
}

// "Faltan 3 días", "Vencido hace 2 días", "Recoger en 1 día"...
function textoTiempo(prestamo) {
    const d = prestamo.dias_restantes;
    if (d === null || d === undefined) return '';
    if (prestamo.estado === 'APARTADO') {
        if (d < 0) return `Plazo para recoger vencido hace ${plural(-d, 'día')}`;
        return d === 0 ? 'Recoger hoy' : `Recoger en ${plural(d, 'día')}`;
    }
    if (d < 0) return `Vencido hace ${plural(-d, 'día')}`;
    return d === 0 ? 'Vence hoy' : `Faltan ${plural(d, 'día')}`;
}

function badgeEstado(prestamo) {
    const tiempo = textoTiempo(prestamo);
    return `<span class="status-badge ${claseEstado(prestamo.estado)}">${esc(prestamo.estado)}</span>`
        + (tiempo ? `<div class="texto-muted">${esc(tiempo)}</div>` : '');
}

function listaTitulos(prestamo) {
    return prestamo.libros.map(l => esc(l.titulo)).join('<br>');
}
