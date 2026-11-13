// =====================================================================
// Panel del personal (bibliotecarios y administradores).
// Requiere sesion.js cargado antes. Cada página solo ejecuta la parte
// cuyo elemento existe (ver "ARRANQUE" al final).
// =====================================================================

const SESION = requerirSesion('personal');
mostrarUsuarioEnMenu(SESION);

function abrirModalEl(id) {
    document.getElementById(id).classList.add('active');
}

function cerrarModalEl(id, formId) {
    document.getElementById(id).classList.remove('active');
    if (formId) document.getElementById(formId).reset();
}

function filaMensaje(tbody, columnas, texto, clase = '') {
    tbody.innerHTML = `<tr><td colspan="${columnas}" class="${clase}">${esc(texto)}</td></tr>`;
}

// ==========================================
// DASHBOARD
// ==========================================
async function cargarDashboard() {
    const tbody = document.getElementById('tabla-dashboard-prestamos');
    try {
        const [libros, prestamos] = await Promise.all([api('/libros/'), api('/prestamos/')]);
        const contar = estado => prestamos.filter(p => p.estado === estado).length;
        document.getElementById('kpi-libros').textContent = libros.length;
        document.getElementById('kpi-disponibles').textContent = libros.filter(l => l.disponible).length;
        document.getElementById('kpi-activos').textContent = contar('ACTIVO');
        document.getElementById('kpi-apartados').textContent = contar('APARTADO');
        document.getElementById('kpi-vencidos').textContent = contar('VENCIDO');

        const recientes = prestamos.slice(0, 5);  // la API ya los manda del más reciente
        if (!recientes.length) return filaMensaje(tbody, 4, 'Todavía no hay préstamos');
        tbody.innerHTML = recientes.map(p => `
            <tr>
                <td><strong>${esc(p.cliente_nombre)}</strong></td>
                <td>#${esc(p.id)}</td>
                <td>${formatoFecha(p.fecha_limite)}</td>
                <td>${badgeEstado(p)}</td>
            </tr>`).join('');
    } catch (error) {
        filaMensaje(tbody, 4, `Error: ${error.message}`, 'mensaje-error');
    }
}

// ==========================================
// LIBROS
// ==========================================
let libros = new Map();
let libroEnEdicion = null;

async function cargarLibros() {
    const tbody = document.getElementById('tabla-libros');
    try {
        const lista = await api('/libros/');
        libros = new Map(lista.map(l => [l.id, l]));
        if (!lista.length) return filaMensaje(tbody, 6, 'No hay libros registrados');
        tbody.innerHTML = lista.map(l => `
            <tr>
                <td><strong>${esc(l.id)}</strong></td>
                <td>${esc(l.titulo)}<div class="texto-muted">${esc(l.categorias || '')}</div></td>
                <td>${esc(l.editorial)}</td>
                <td>${esc(l.anio ?? '—')}</td>
                <td><span class="status-badge ${l.disponible ? 'green' : 'red'}">
                    ${l.disponible ? 'Disponible' : 'No disponible'}</span></td>
                <td>
                    <button class="btn-edit" data-accion="editar" data-id="${esc(l.id)}">Editar</button>
                    <button class="btn-danger" data-accion="eliminar" data-id="${esc(l.id)}">Eliminar</button>
                </td>
            </tr>`).join('');
    } catch (error) {
        filaMensaje(tbody, 6, `Error: ${error.message}`, 'mensaje-error');
    }
}

async function cargarEditoriales() {
    try {
        const editoriales = await api('/editoriales/');
        llenarSelect(document.getElementById('libro-editorial'),
            editoriales.map(e => ({ value: e.id, text: `${e.nombre} (${e.id})` })),
            'Selecciona la editorial');
    } catch (error) {
        alert(error.message);
    }
}

function abrirModal(modo, id) {
    libroEnEdicion = modo === 'editar' ? libros.get(id) : null;
    const l = libroEnEdicion || {};
    document.getElementById('modal-titulo').textContent = libroEnEdicion ? 'Editar Libro' : 'Nuevo Libro';
    document.getElementById('libro-id').value = l.id || '';
    document.getElementById('libro-id').disabled = Boolean(libroEnEdicion);
    document.getElementById('libro-titulo').value = l.titulo || '';
    document.getElementById('libro-anio').value = l.anio ?? '';
    document.getElementById('libro-editorial').value = l.editorial_id || '';
    document.getElementById('libro-estado').value = String(l.disponible ?? true);
    abrirModalEl('modal-libro');
}

function cerrarModal() {
    cerrarModalEl('modal-libro', 'form-libro');
}

async function guardarLibro(e) {
    e.preventDefault();
    const anio = document.getElementById('libro-anio').value;
    const datos = {
        editorial_id: document.getElementById('libro-editorial').value,
        titulo: document.getElementById('libro-titulo').value,
        anio: anio ? parseInt(anio, 10) : null,
        disponible: document.getElementById('libro-estado').value === 'true',
    };
    try {
        if (libroEnEdicion) {
            await api(`/libros/${encodeURIComponent(libroEnEdicion.id)}`, { method: 'PUT', body: datos });
        } else {
            datos.id = document.getElementById('libro-id').value;
            await api('/libros/', { method: 'POST', body: datos });
        }
        cerrarModal();
        cargarLibros();
    } catch (error) {
        alert(error.message);
    }
}

async function eliminarLibro(id) {
    if (!confirm(`¿Eliminar el libro ${id}?`)) return;
    try {
        await api(`/libros/${encodeURIComponent(id)}`, { method: 'DELETE' });
        cargarLibros();
    } catch (error) {
        alert(error.message);
    }
}

// ==========================================
// USUARIOS (personal)
// ==========================================
let usuarios = new Map();
let usuarioEnEdicion = null;

async function cargarUsuarios() {
    const tbody = document.getElementById('tabla-usuarios');
    try {
        const lista = await api('/usuarios/');
        usuarios = new Map(lista.map(u => [u.id, u]));
        tbody.innerHTML = lista.map(u => `
            <tr>
                <td><strong>${esc(u.username)}</strong><div class="texto-muted">${esc(u.id)}</div></td>
                <td>${esc(u.nombre)} ${esc(u.apellido_p)} ${esc(u.apellido_m || '')}</td>
                <td><span class="status-badge blue">${esc(u.cargo)}</span></td>
                <td>
                    <button class="btn-edit" data-accion="editar" data-id="${esc(u.id)}">Editar</button>
                    <button class="btn-danger" data-accion="eliminar" data-id="${esc(u.id)}">Eliminar</button>
                </td>
            </tr>`).join('');
    } catch (error) {
        filaMensaje(tbody, 4, `Error: ${error.message}`, 'mensaje-error');
    }
}

async function cargarCargos() {
    try {
        const cargos = await api('/usuarios/cargos');
        llenarSelect(document.getElementById('usr-cargo'),
            cargos.map(c => ({ value: c.id, text: c.puesto })), 'Selecciona el cargo');
    } catch (error) {
        alert(error.message);
    }
}

function abrirModalUsuario(modo, id) {
    usuarioEnEdicion = modo === 'editar' ? usuarios.get(id) : null;
    const u = usuarioEnEdicion || {};
    document.getElementById('modal-usuario-titulo').textContent =
        usuarioEnEdicion ? 'Editar Usuario' : 'Nuevo Usuario';
    document.getElementById('usr-id').value = u.id || '';
    document.getElementById('usr-id').disabled = Boolean(usuarioEnEdicion);
    document.getElementById('usr-cargo').value = u.cargo_id || '';
    document.getElementById('usr-username').value = u.username || '';
    // La contraseña nunca viene del servidor: al editar, vacía = no cambiarla
    const password = document.getElementById('usr-password');
    password.value = '';
    password.required = !usuarioEnEdicion;
    password.placeholder = usuarioEnEdicion
        ? 'Nueva contraseña (vacío = no cambiar)' : 'Contraseña (mínimo 6 caracteres)';
    document.getElementById('usr-nombre').value = u.nombre || '';
    document.getElementById('usr-apellidop').value = u.apellido_p || '';
    document.getElementById('usr-apellidom').value = u.apellido_m || '';
    abrirModalEl('modal-usuario');
}

function cerrarModalUsuario() {
    cerrarModalEl('modal-usuario', 'form-usuario');
}

async function guardarUsuario(e) {
    e.preventDefault();
    const datos = {
        cargo_id: document.getElementById('usr-cargo').value,
        username: document.getElementById('usr-username').value,
        nombre: document.getElementById('usr-nombre').value,
        apellido_p: document.getElementById('usr-apellidop').value,
        apellido_m: document.getElementById('usr-apellidom').value,
    };
    const password = document.getElementById('usr-password').value;
    if (password) datos.password = password;
    try {
        if (usuarioEnEdicion) {
            await api(`/usuarios/${encodeURIComponent(usuarioEnEdicion.id)}`, { method: 'PUT', body: datos });
        } else {
            datos.id = document.getElementById('usr-id').value;
            await api('/usuarios/', { method: 'POST', body: datos });
        }
        cerrarModalUsuario();
        cargarUsuarios();
    } catch (error) {
        alert(error.message);
    }
}

async function eliminarUsuario(id) {
    if (!confirm(`¿Eliminar al usuario ${id}?`)) return;
    try {
        await api(`/usuarios/${encodeURIComponent(id)}`, { method: 'DELETE' });
        cargarUsuarios();
    } catch (error) {
        alert(error.message);
    }
}

// ==========================================
// CLIENTES
// ==========================================
let clientes = new Map();
let clienteEnEdicion = null;

async function cargarClientes() {
    const tbody = document.getElementById('tabla-clientes');
    try {
        const lista = await api('/clientes/');
        clientes = new Map(lista.map(c => [c.id, c]));
        tbody.innerHTML = lista.map(c => `
            <tr>
                <td><strong>${esc(c.id)}</strong></td>
                <td>${esc(c.nombre)} ${esc(c.apellido_p)} ${esc(c.apellido_m || '')}</td>
                <td>${esc(c.correo)}</td>
                <td>${esc(c.telefono || '—')}</td>
                <td><span class="status-badge ${c.acceso_portal ? 'green' : 'gray'}">
                    ${c.acceso_portal ? 'Sí' : 'No'}</span></td>
                <td>
                    <button class="btn-edit" data-accion="editar" data-id="${esc(c.id)}">Editar</button>
                    <button class="btn-danger" data-accion="eliminar" data-id="${esc(c.id)}">Eliminar</button>
                </td>
            </tr>`).join('');
    } catch (error) {
        filaMensaje(tbody, 6, `Error: ${error.message}`, 'mensaje-error');
    }
}

function abrirModalCliente(modo, id) {
    clienteEnEdicion = modo === 'editar' ? clientes.get(id) : null;
    const c = clienteEnEdicion || {};
    document.getElementById('modal-cliente-titulo').textContent =
        clienteEnEdicion ? 'Editar Cliente' : 'Nuevo Cliente';
    document.getElementById('cli-id').value = c.id || '';
    document.getElementById('cli-id').disabled = Boolean(clienteEnEdicion);
    document.getElementById('cli-nombre').value = c.nombre || '';
    document.getElementById('cli-apellidop').value = c.apellido_p || '';
    document.getElementById('cli-apellidom').value = c.apellido_m || '';
    document.getElementById('cli-correo').value = c.correo || '';
    document.getElementById('cli-telefono').value = c.telefono || '';
    document.getElementById('cli-password').value = '';
    document.getElementById('cli-password').placeholder = clienteEnEdicion && c.acceso_portal
        ? 'Nueva contraseña del portal (vacío = no cambiar)'
        : 'Contraseña del portal (opcional, mínimo 6)';
    abrirModalEl('modal-cliente');
}

function cerrarModalCliente() {
    cerrarModalEl('modal-cliente', 'form-cliente');
}

async function guardarCliente(e) {
    e.preventDefault();
    const datos = {
        nombre: document.getElementById('cli-nombre').value,
        apellido_p: document.getElementById('cli-apellidop').value,
        apellido_m: document.getElementById('cli-apellidom').value,
        correo: document.getElementById('cli-correo').value,
        telefono: document.getElementById('cli-telefono').value,
    };
    const password = document.getElementById('cli-password').value;
    if (password) datos.password = password;
    try {
        if (clienteEnEdicion) {
            await api(`/clientes/${encodeURIComponent(clienteEnEdicion.id)}`, { method: 'PUT', body: datos });
        } else {
            datos.id = document.getElementById('cli-id').value;
            await api('/clientes/', { method: 'POST', body: datos });
        }
        cerrarModalCliente();
        cargarClientes();
    } catch (error) {
        alert(error.message);
    }
}

async function eliminarCliente(id) {
    if (!confirm(`¿Eliminar al cliente ${id}?`)) return;
    try {
        await api(`/clientes/${encodeURIComponent(id)}`, { method: 'DELETE' });
        cargarClientes();
    } catch (error) {
        alert(error.message);
    }
}

// ==========================================
// CATEGORÍAS
// ==========================================
let categorias = new Map();
let categoriaEnEdicion = null;

async function cargarCategorias() {
    const tbody = document.getElementById('tabla-categorias');
    try {
        const lista = await api('/categorias/');
        categorias = new Map(lista.map(c => [c.id, c]));
        tbody.innerHTML = lista.map(c => `
            <tr>
                <td><strong>${esc(c.id)}</strong></td>
                <td>${esc(c.nombre)}</td>
                <td>
                    <button class="btn-edit" data-accion="editar" data-id="${esc(c.id)}">Editar</button>
                    <button class="btn-danger" data-accion="eliminar" data-id="${esc(c.id)}">Eliminar</button>
                </td>
            </tr>`).join('');
    } catch (error) {
        filaMensaje(tbody, 3, `Error: ${error.message}`, 'mensaje-error');
    }
}

function abrirModalCat(modo, id) {
    categoriaEnEdicion = modo === 'editar' ? categorias.get(id) : null;
    const c = categoriaEnEdicion || {};
    document.getElementById('modal-cat-titulo').textContent =
        categoriaEnEdicion ? 'Editar Categoría' : 'Nueva Categoría';
    document.getElementById('cat-id').value = c.id || '';
    document.getElementById('cat-id').disabled = Boolean(categoriaEnEdicion);
    document.getElementById('cat-nombre').value = c.nombre || '';
    abrirModalEl('modal-categoria');
}

function cerrarModalCat() {
    cerrarModalEl('modal-categoria', 'form-categoria');
}

async function guardarCategoria(e) {
    e.preventDefault();
    const nombre = document.getElementById('cat-nombre').value;
    try {
        if (categoriaEnEdicion) {
            await api(`/categorias/${encodeURIComponent(categoriaEnEdicion.id)}`,
                { method: 'PUT', body: { nombre } });
        } else {
            await api('/categorias/', {
                method: 'POST', body: { id: document.getElementById('cat-id').value, nombre },
            });
        }
        cerrarModalCat();
        cargarCategorias();
    } catch (error) {
        alert(error.message);
    }
}

async function eliminarCategoria(id) {
    if (!confirm(`¿Eliminar la categoría ${id}?`)) return;
    try {
        await api(`/categorias/${encodeURIComponent(id)}`, { method: 'DELETE' });
        cargarCategorias();
    } catch (error) {
        alert(error.message);
    }
}

// ==========================================
// PRÉSTAMOS
// ==========================================
let prestamos = new Map();
let prestamoEnEdicion = null;

function accionesPrestamo(p) {
    const id = esc(p.id);
    const botones = [];
    if (p.estado === 'APARTADO') {
        botones.push(`<button class="btn-success" data-accion="entregar" data-id="${id}">Entregar</button>`);
    }
    if (p.estado === 'ACTIVO' || p.estado === 'VENCIDO') {
        botones.push(`<button class="btn-success" data-accion="devolver" data-id="${id}">Devolver</button>`);
        botones.push(`<button class="btn-edit" data-accion="fechas" data-id="${id}">Renovar</button>`);
    }
    const textoEliminar = p.estado === 'APARTADO' ? 'Cancelar' : 'Eliminar';
    botones.push(`<button class="btn-danger" data-accion="eliminar" data-id="${id}">${textoEliminar}</button>`);
    return botones.join(' ');
}

async function cargarPrestamos() {
    const tbody = document.getElementById('tabla-prestamos');
    const filtro = document.getElementById('filtro-estado').value;
    try {
        const lista = await api('/prestamos/');
        prestamos = new Map(lista.map(p => [p.id, p]));
        const visibles = filtro ? lista.filter(p => p.estado === filtro) : lista;
        if (!visibles.length) return filaMensaje(tbody, 7, 'No hay préstamos con ese estado');
        tbody.innerHTML = visibles.map(p => `
            <tr>
                <td><strong>#${esc(p.id)}</strong></td>
                <td>${esc(p.cliente_nombre)}<div class="texto-muted">${esc(p.cliente_id)}</div></td>
                <td>${listaTitulos(p)}</td>
                <td>${formatoFecha(p.fecha_prestamo)}</td>
                <td>${formatoFecha(p.fecha_limite)}</td>
                <td>${badgeEstado(p)}</td>
                <td class="acciones">${accionesPrestamo(p)}</td>
            </tr>`).join('');
    } catch (error) {
        filaMensaje(tbody, 7, `Error: ${error.message}`, 'mensaje-error');
    }
}

async function abrirModalPrestamo() {
    try {
        const [listaClientes, disponibles] = await Promise.all([
            api('/clientes/'), api('/libros/?solo_disponibles=true'),
        ]);
        llenarSelect(document.getElementById('prest-cliente'),
            listaClientes.map(c => ({ value: c.id, text: `${c.nombre} ${c.apellido_p} (${c.id})` })),
            'Selecciona el cliente');
        const contenedor = document.getElementById('prest-libros');
        contenedor.innerHTML = disponibles.length
            ? disponibles.map(l => `
                <label><input type="checkbox" value="${esc(l.id)}">
                    ${esc(l.titulo)} <span class="texto-muted">(${esc(l.id)})</span></label>`).join('')
            : '<p class="texto-muted">No hay libros disponibles</p>';
        abrirModalEl('modal-prestamo');
    } catch (error) {
        alert(error.message);
    }
}

function cerrarModalPrestamo() {
    cerrarModalEl('modal-prestamo', 'form-prestamo');
}

async function guardarPrestamo(e) {
    e.preventDefault();
    const libros = [...document.querySelectorAll('#prest-libros input:checked')].map(c => c.value);
    if (!libros.length) return alert('Selecciona al menos un libro.');
    const datos = { cliente_id: document.getElementById('prest-cliente').value, libros };
    const fechaLimite = document.getElementById('prest-fechal').value;
    if (fechaLimite) datos.fecha_limite = fechaLimite;
    try {
        await api('/prestamos/', { method: 'POST', body: datos });
        cerrarModalPrestamo();
        cargarPrestamos();
    } catch (error) {
        alert(error.message);
    }
}

function abrirModalFechas(id) {
    prestamoEnEdicion = prestamos.get(id);
    document.getElementById('fechas-titulo').textContent = `Renovar préstamo #${id}`;
    document.getElementById('fechas-prestamo').value = prestamoEnEdicion.fecha_prestamo;
    document.getElementById('fechas-limite').value = prestamoEnEdicion.fecha_limite;
    abrirModalEl('modal-fechas');
}

function cerrarModalFechas() {
    cerrarModalEl('modal-fechas', 'form-fechas');
}

async function guardarFechas(e) {
    e.preventDefault();
    try {
        await api(`/prestamos/${encodeURIComponent(prestamoEnEdicion.id)}`, {
            method: 'PUT',
            body: {
                fecha_prestamo: document.getElementById('fechas-prestamo').value,
                fecha_limite: document.getElementById('fechas-limite').value,
            },
        });
        cerrarModalFechas();
        cargarPrestamos();
    } catch (error) {
        alert(error.message);
    }
}

async function accionPrestamo(id, accion, pregunta) {
    if (!confirm(pregunta)) return;
    try {
        await api(`/prestamos/${encodeURIComponent(id)}/${accion}`, { method: 'PUT' });
        cargarPrestamos();
    } catch (error) {
        alert(error.message);
    }
}

async function eliminarPrestamo(id) {
    const p = prestamos.get(id);
    const pregunta = p && p.estado === 'APARTADO'
        ? `¿Cancelar el apartado #${id}? Los libros vuelven a estar disponibles.`
        : `¿Eliminar el préstamo #${id} del historial?`;
    if (!confirm(pregunta)) return;
    try {
        await api(`/prestamos/${encodeURIComponent(id)}`, { method: 'DELETE' });
        cargarPrestamos();
    } catch (error) {
        alert(error.message);
    }
}

// ==========================================
// ARRANQUE (según los elementos que tenga la página)
// ==========================================
function siExiste(id, fn) {
    const el = document.getElementById(id);
    if (el) fn(el);
}

if (SESION) {
    siExiste('tabla-dashboard-prestamos', () => cargarDashboard());

    siExiste('tabla-libros', (tbody) => {
        cargarLibros();
        cargarEditoriales();
        delegarAcciones(tbody, { editar: id => abrirModal('editar', id), eliminar: eliminarLibro });
        document.getElementById('form-libro').addEventListener('submit', guardarLibro);
    });

    siExiste('tabla-usuarios', (tbody) => {
        cargarUsuarios();
        cargarCargos();
        delegarAcciones(tbody, {
            editar: id => abrirModalUsuario('editar', id), eliminar: eliminarUsuario,
        });
        document.getElementById('form-usuario').addEventListener('submit', guardarUsuario);
    });

    siExiste('tabla-clientes', (tbody) => {
        cargarClientes();
        delegarAcciones(tbody, {
            editar: id => abrirModalCliente('editar', id), eliminar: eliminarCliente,
        });
        document.getElementById('form-cliente').addEventListener('submit', guardarCliente);
    });

    siExiste('tabla-categorias', (tbody) => {
        cargarCategorias();
        delegarAcciones(tbody, {
            editar: id => abrirModalCat('editar', id), eliminar: eliminarCategoria,
        });
        document.getElementById('form-categoria').addEventListener('submit', guardarCategoria);
    });

    siExiste('tabla-prestamos', (tbody) => {
        cargarPrestamos();
        delegarAcciones(tbody, {
            entregar: id => accionPrestamo(id, 'entregar',
                `¿El cliente recogió el apartado #${id}? El préstamo empieza a contar desde hoy.`),
            devolver: id => accionPrestamo(id, 'devolver',
                `¿Registrar la devolución del préstamo #${id}?`),
            fechas: abrirModalFechas,
            eliminar: eliminarPrestamo,
        });
        document.getElementById('filtro-estado').addEventListener('change', cargarPrestamos);
        document.getElementById('form-prestamo').addEventListener('submit', guardarPrestamo);
        document.getElementById('form-fechas').addEventListener('submit', guardarFechas);
    });
}
