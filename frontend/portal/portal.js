// =====================================================================
// Portal de clientes: mis préstamos (con tiempo restante) y apartar libros.
// Requiere sesion.js cargado antes.
// =====================================================================

const SESION = requerirSesion('cliente');
mostrarUsuarioEnMenu(SESION);

let catalogo = [];

function mostrarAviso(texto, tipo) {
    const aviso = document.getElementById('aviso');
    aviso.textContent = texto;
    aviso.className = `aviso ${tipo}`;
    aviso.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function cargarMisPrestamos() {
    const tbody = document.getElementById('tabla-mis-prestamos');
    try {
        const prestamos = await api('/mi/prestamos');
        const contar = estado => prestamos.filter(p => p.estado === estado).length;
        document.getElementById('kpi-apartados').textContent = contar('APARTADO');
        document.getElementById('kpi-activos').textContent = contar('ACTIVO');
        document.getElementById('kpi-vencidos').textContent = contar('VENCIDO');

        if (!prestamos.length) {
            tbody.innerHTML = '<tr><td colspan="6">Aún no tienes préstamos. Aparta libros del catálogo.</td></tr>';
            return;
        }
        tbody.innerHTML = prestamos.map(p => `
            <tr>
                <td><strong>#${esc(p.id)}</strong></td>
                <td>${listaTitulos(p)}</td>
                <td>${formatoFecha(p.fecha_prestamo)}</td>
                <td>${formatoFecha(p.estado === 'DEVUELTO' ? p.fecha_devolucion : p.fecha_limite)}</td>
                <td>${badgeEstado(p)}</td>
                <td>${p.estado === 'APARTADO'
                    ? `<button class="btn-danger" data-accion="cancelar" data-id="${esc(p.id)}">Cancelar</button>`
                    : ''}</td>
            </tr>`).join('');
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="6" class="mensaje-error">${esc(error.message)}</td></tr>`;
    }
}

function pintarCatalogo() {
    const tbody = document.getElementById('tabla-catalogo');
    const texto = document.getElementById('buscar').value.trim().toLowerCase();
    const visibles = catalogo.filter(l =>
        [l.titulo, l.editorial, l.categorias].join(' ').toLowerCase().includes(texto));
    if (!visibles.length) {
        tbody.innerHTML = '<tr><td colspan="6">No se encontraron libros</td></tr>';
        return;
    }
    tbody.innerHTML = visibles.map(l => `
        <tr>
            <td>${l.disponible
                ? `<input type="checkbox" class="elegir-libro" value="${esc(l.id)}" aria-label="Apartar ${esc(l.titulo)}">`
                : ''}</td>
            <td><strong>${esc(l.titulo)}</strong></td>
            <td>${esc(l.editorial)}</td>
            <td>${esc(l.categorias || '—')}</td>
            <td>${esc(l.anio ?? '—')}</td>
            <td><span class="status-badge ${l.disponible ? 'green' : 'gray'}">
                ${l.disponible ? 'Disponible' : 'Prestado'}</span></td>
        </tr>`).join('');
    actualizarBotonApartar();
}

async function cargarCatalogo() {
    try {
        catalogo = await api('/libros/');
        pintarCatalogo();
    } catch (error) {
        document.getElementById('tabla-catalogo').innerHTML =
            `<tr><td colspan="6" class="mensaje-error">${esc(error.message)}</td></tr>`;
    }
}

function seleccionados() {
    return [...document.querySelectorAll('.elegir-libro:checked')].map(c => c.value);
}

function actualizarBotonApartar() {
    const n = seleccionados().length;
    const boton = document.getElementById('btn-apartar');
    boton.disabled = n === 0;
    boton.textContent = n ? `Apartar ${plural(n, 'libro')}` : 'Apartar seleccionados';
}

async function apartar() {
    const libros = seleccionados();
    if (!libros.length) return;
    const boton = document.getElementById('btn-apartar');
    boton.disabled = true;
    try {
        const r = await api('/mi/prestamos', { method: 'POST', body: { libros } });
        mostrarAviso(`Apartado #${r.id}: ${r.mensaje}`, 'ok');
    } catch (error) {
        mostrarAviso(error.message, 'error');
    } finally {
        await Promise.all([cargarMisPrestamos(), cargarCatalogo()]);
    }
}

async function cancelar(id) {
    if (!confirm(`¿Cancelar el apartado #${id}?`)) return;
    try {
        await api(`/mi/prestamos/${encodeURIComponent(id)}`, { method: 'DELETE' });
        mostrarAviso(`Apartado #${id} cancelado.`, 'ok');
    } catch (error) {
        mostrarAviso(error.message, 'error');
    }
    await Promise.all([cargarMisPrestamos(), cargarCatalogo()]);
}

if (SESION) {
    document.getElementById('saludo').textContent = `Hola, ${SESION.nombre}`;
    cargarMisPrestamos();
    cargarCatalogo();
    delegarAcciones(document.getElementById('tabla-mis-prestamos'), { cancelar });
    document.getElementById('tabla-catalogo').addEventListener('change', actualizarBotonApartar);
    document.getElementById('buscar').addEventListener('input', pintarCatalogo);
    document.getElementById('btn-apartar').addEventListener('click', apartar);
}
