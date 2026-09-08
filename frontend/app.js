const API_URL = 'http://localhost:8000';

async function obtenerDatos(endpoint) {
    const res = await fetch(`${API_URL}${endpoint}`);
    if (!res.ok) throw new Error(`Error ${res.status}`);
    return await res.json();
}

// ------------------------------------------
// LÓGICA DE DIBUJO DE TABLAS Y DASHBOARD
// ------------------------------------------
async function cargarDashboard() {
    try {
        const [libros, prestamos, usuarios] = await Promise.all([
            obtenerDatos('/libros'),
            obtenerDatos('/prestamos'),
            obtenerDatos('/usuarios'),
        ]);
        document.getElementById('kpi-libros').innerText = libros.length;
        document.getElementById('kpi-disponibles').innerText = libros.filter(l => l.disponible).length;
        document.getElementById('kpi-activos').innerText = prestamos.filter(p => p.estado.toUpperCase() === 'ACTIVO').length;
        document.getElementById('kpi-usuarios').innerText = usuarios.length;
        document.getElementById('kpi-vencidos').innerText = prestamos.filter(p => p.estado.toUpperCase() === 'VENCIDO').length;

        const tbody = document.getElementById('tabla-dashboard-prestamos');
        tbody.innerHTML = '';
        prestamos.slice(-3).reverse().forEach(p => {
            let badgeClass = p.estado.toUpperCase() === 'VENCIDO' ? 'red' : 'blue';
            tbody.innerHTML += `<tr><td><strong>${p.cliente_nombre}</strong></td><td>#${p.id}</td><td>${p.fecha_prestamo}</td><td><span class="status-badge ${badgeClass}">${p.estado}</span></td></tr>`;
        });
    } catch (error) { console.error("Error Dashboard:", error); }
}

async function cargarLibros() {
    const tbody = document.getElementById('tabla-libros');
    if (!tbody) return;
    try {
        const libros = await obtenerDatos('/libros');
        tbody.innerHTML = '';
        libros.forEach(libro => {
            let badgeClass = libro.disponible ? 'green' : 'red';
            let textoDisp = libro.disponible ? 'Disponible' : 'No disponible';

            tbody.innerHTML += `
                <tr>
                    <td><strong>${libro.id}</strong></td>
                    <td>${libro.titulo}</td>
                    <td>${libro.anio}</td>
                    <td><span class="status-badge ${badgeClass}">${textoDisp}</span></td>
                    <td>
                        <button class="btn-edit" onclick="abrirModal('editar', '${libro.id}', '${libro.titulo}', ${libro.anio}, '${libro.editorial_id}', ${libro.disponible})">Editar</button>
                        <button class="btn-danger" onclick="eliminarLibro('${libro.id}')">Eliminar</button>
                    </td>
                </tr>
            `;
        });
    } catch (error) { tbody.innerHTML = `<tr><td colspan="5" class="mensaje-error">Error: ${error.message}</td></tr>`; }
}

// ==========================================
// RENDERIZADO DE TABLAS
// ==========================================
async function cargarUsuarios() {
    const tbody = document.getElementById('tabla-usuarios');
    if (!tbody) return;
    try {
        const usuarios = await obtenerDatos('/usuarios');
        tbody.innerHTML = '';
        usuarios.forEach(u => {
            tbody.innerHTML += `
                <tr>
                    <td><strong>${u.username}</strong></td>
                    <td>${u.nombre} ${u.apellido_p}</td>
                    <td><span class="status-badge blue">${u.cargo}</span></td>
                    <td>
                        <button class="btn-edit" onclick="abrirModalUsuario('editar', '${u.id}', '${u.cargo_id}', '${u.username}', '', '${u.nombre}', '${u.apellido_p}', '${u.apellido_m || ''}')">Editar</button>
                        <button class="btn-danger" onclick="eliminarUsuario('${u.id}')">Eliminar</button>
                    </td>
                </tr>`;
        });
    } catch (error) { tbody.innerHTML = `<tr><td colspan="4" class="mensaje-error">Error: ${error.message}</td></tr>`; }
}

async function cargarPrestamos() {
    const tbody = document.getElementById('tabla-prestamos');
    if (!tbody) return;
    try {
        const prestamos = await obtenerDatos('/prestamos');
        tbody.innerHTML = '';
        prestamos.forEach(p => {
            let badgeClass = p.estado.toUpperCase() === 'VENCIDO' ? 'red' : 'blue';
            tbody.innerHTML += `
                <tr>
                    <td><strong>#${p.id}</strong></td>
                    <td>${p.cliente_nombre}</td>
                    <td>${p.fecha_prestamo}</td>
                    <td><span class="status-badge ${badgeClass}">${p.estado}</span></td>
                    <td>
                        <button class="btn-edit" onclick="abrirModalPrestamo('editar', '${p.id}', '${p.estado_id}', '${p.cliente_id}', '${p.usuario_id}', '${p.fecha_prestamo}', '${p.fecha_devolucion || ''}')">Editar</button>
                        <button class="btn-danger" onclick="eliminarPrestamo('${p.id}')">Eliminar</button>
                    </td>
                </tr>`;
        });
    } catch (error) { tbody.innerHTML = `<tr><td colspan="5" class="mensaje-error">Error: ${error.message}</td></tr>`; }
}

// ==========================================
// FORMULARIO DE USUARIOS (AGREGAR Y EDITAR)
// ==========================================
let modoEdicionUsuario = false;

function abrirModalUsuario(modo, id='', cargo='', username='', password='', nombre='', ap='', am='') {
    modoEdicionUsuario = (modo === 'editar');
    const titulo = document.querySelector('#modal-usuario h2');
    if (titulo) titulo.innerText = modoEdicionUsuario ? 'Editar Usuario' : 'Nuevo Usuario';

    document.getElementById('usr-id').value = id;
    document.getElementById('usr-id').disabled = modoEdicionUsuario;
    document.getElementById('usr-cargo').value = cargo;
    document.getElementById('usr-username').value = username;
    document.getElementById('usr-password').value = password;
    document.getElementById('usr-nombre').value = nombre;
    document.getElementById('usr-apellidop').value = ap;
    document.getElementById('usr-apellidom').value = am;

    document.getElementById('modal-usuario').classList.add('active');
}

function cerrarModalUsuario() {
    document.getElementById('modal-usuario').classList.remove('active');
    document.getElementById('form-usuario').reset();
}

document.getElementById('form-usuario')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('usr-id').value;
    const data = {
        id: id,
        cargo_id: document.getElementById('usr-cargo').value,
        username: document.getElementById('usr-username').value,
        password: document.getElementById('usr-password').value,
        nombre: document.getElementById('usr-nombre').value,
        apellido_p: document.getElementById('usr-apellidop').value,
        apellido_m: document.getElementById('usr-apellidom').value
    };
    // Si estamos editando y no se escribió una contraseña nueva, no la mandamos
    if (modoEdicionUsuario && !data.password) delete data.password;

    const metodo = modoEdicionUsuario ? 'PUT' : 'POST';
    const endpoint = modoEdicionUsuario ? `/usuarios/${id}` : '/usuarios';

    try {
        const res = await fetch(`${API_URL}${endpoint}`, {
            method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Error al guardar. Revisa que el ID del Cargo exista en tu Base de Datos.");
        cerrarModalUsuario();
        cargarUsuarios();
        if (document.getElementById('kpi-usuarios')) cargarDashboard();
    } catch (error) { alert(error.message); }
});

// ==========================================
// FORMULARIO DE PRÉSTAMOS (AGREGAR Y EDITAR)
// ==========================================
let modoEdicionPrestamo = false;

function abrirModalPrestamo(modo, id='', estado='', cliente='', usuario='', fechap='', fechad='') {
    modoEdicionPrestamo = (modo === 'editar');
    document.getElementById('modal-prestamo-titulo').innerText = modoEdicionPrestamo ? 'Editar Préstamo' : 'Nuevo Préstamo';

    document.getElementById('prest-id').value = id;
    document.getElementById('prest-id').disabled = modoEdicionPrestamo;
    document.getElementById('prest-estado').value = estado;
    document.getElementById('prest-cliente').value = cliente;
    document.getElementById('prest-usuario').value = usuario;
    document.getElementById('prest-fechap').value = fechap;
    document.getElementById('prest-fechad').value = fechad;

    document.getElementById('modal-prestamo').classList.add('active');
}

function cerrarModalPrestamo() {
    document.getElementById('modal-prestamo').classList.remove('active');
    document.getElementById('form-prestamo').reset();
}

document.getElementById('form-prestamo')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('prest-id').value;
    const fechaDevolucion = document.getElementById('prest-fechad').value;
    const data = {
        id: id || undefined,
        estado_prestamos_id: document.getElementById('prest-estado').value,
        cliente_id: document.getElementById('prest-cliente').value,
        usuario_id: document.getElementById('prest-usuario').value,
        fecha_prestamo: document.getElementById('prest-fechap').value,
        // Un string vacío no es una fecha válida para el backend: mandamos null en ese caso
        fecha_devolucion: fechaDevolucion ? fechaDevolucion : null
    };

    const metodo = modoEdicionPrestamo ? 'PUT' : 'POST';
    const endpoint = modoEdicionPrestamo ? `/prestamos/${id}` : '/prestamos';

    try {
        const res = await fetch(`${API_URL}${endpoint}`, {
            method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Error al guardar. Verifica que el Cliente, Estado y Usuario existan.");
        cerrarModalPrestamo();
        cargarPrestamos();
        if (document.getElementById('kpi-libros')) cargarDashboard();
    } catch (error) { alert(error.message); }
});

// ------------------------------------------
// LÓGICA DE CRUD DE LIBROS
// ------------------------------------------
let modoEdicion = false;

function abrirModal(modo, id='', titulo='', anio='', editorial='', disponible=true) {
    modoEdicion = (modo === 'editar');
    document.getElementById('modal-titulo').innerText = modoEdicion ? 'Editar Libro' : 'Nuevo Libro';
    document.getElementById('libro-id').value = id;
    document.getElementById('libro-id').disabled = modoEdicion; // Bloquear ID si estamos editando
    document.getElementById('libro-titulo').value = titulo;
    document.getElementById('libro-anio').value = anio;
    document.getElementById('libro-editorial').value = editorial;
    document.getElementById('libro-estado').value = disponible;

    document.getElementById('modal-libro').classList.add('active');
}

function cerrarModal() {
    document.getElementById('modal-libro').classList.remove('active');
    document.getElementById('form-libro').reset();
}

document.getElementById('form-libro')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('libro-id').value;
    const libroData = {
        id: id,
        editorial_id: document.getElementById('libro-editorial').value,
        titulo: document.getElementById('libro-titulo').value,
        anio: parseInt(document.getElementById('libro-anio').value),
        disponible: document.getElementById('libro-estado').value === 'true'
    };

    const metodo = modoEdicion ? 'PUT' : 'POST';
    const endpoint = modoEdicion ? `/libros/${id}` : '/libros';

    try {
        const res = await fetch(`${API_URL}${endpoint}`, {
            method: metodo,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(libroData)
        });
        if (!res.ok) throw new Error("Revisa que el ID de Editorial exista y que el ID del libro no esté repetido.");
        cerrarModal();
        cargarLibros();
        if (document.getElementById('kpi-libros')) cargarDashboard();
    } catch (error) { alert(error.message); }
});

async function eliminarLibro(id) {
    if (!confirm(`¿Estás seguro de eliminar el libro ${id}?`)) return;
    try {
        const res = await fetch(`${API_URL}/libros/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error("No se pudo eliminar el libro (puede que esté asignado a un préstamo).");
        cargarLibros();
        if (document.getElementById('kpi-libros')) cargarDashboard();
    } catch (error) { alert(error.message); }
}

async function eliminarUsuario(id) {
    if (!confirm(`¿Eliminar al usuario ${id}?`)) return;
    try {
        const res = await fetch(`${API_URL}/usuarios/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error("No se puede eliminar (quizás tiene préstamos asociados).");
        cargarUsuarios();
        if (document.getElementById('kpi-usuarios')) cargarDashboard();
    } catch (error) { alert(error.message); }
}

async function eliminarPrestamo(id) {
    if (!confirm(`¿Eliminar el préstamo ${id}?`)) return;
    try {
        const res = await fetch(`${API_URL}/prestamos/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error("No se pudo eliminar el préstamo.");
        cargarPrestamos();
        if (document.getElementById('kpi-libros')) cargarDashboard();
    } catch (error) { alert(error.message); }
}

// ==========================================
// LÓGICA DE CLIENTES (CRUD COMPLETO)
// ==========================================
let modoEdicionCliente = false;

async function cargarClientes() {
    const tbody = document.getElementById('tabla-clientes');
    if (!tbody) return;
    try {
        const clientes = await obtenerDatos('/clientes');
        tbody.innerHTML = '';
        clientes.forEach(c => {
            tbody.innerHTML += `
                <tr>
                    <td><strong>${c.id}</strong></td>
                    <td>${c.nombre} ${c.apellido_p}</td>
                    <td>${c.correo}</td>
                    <td>${c.telefono || ''}</td>
                    <td>
                        <button class="btn-edit" onclick="abrirModalCliente('editar', '${c.id}', '${c.nombre}', '${c.correo}', '${c.telefono || ''}', '${c.apellido_p}', '${c.apellido_m || ''}')">Editar</button>
                        <button class="btn-danger" onclick="eliminarCliente('${c.id}')">Eliminar</button>
                    </td>
                </tr>`;
        });
    } catch (error) { tbody.innerHTML = `<tr><td colspan="5" class="mensaje-error">Error: ${error.message}</td></tr>`; }
}

function abrirModalCliente(modo, id='', nombre='', correo='', telefono='', ap='', am='') {
    modoEdicionCliente = (modo === 'editar');
    document.getElementById('modal-cliente-titulo').innerText = modoEdicionCliente ? 'Editar Cliente' : 'Nuevo Cliente';

    document.getElementById('cli-id').value = id;
    document.getElementById('cli-id').disabled = modoEdicionCliente;
    document.getElementById('cli-nombre').value = nombre;
    document.getElementById('cli-correo').value = correo;
    document.getElementById('cli-telefono').value = telefono;
    document.getElementById('cli-apellidop').value = ap;
    document.getElementById('cli-apellidom').value = am;

    document.getElementById('modal-cliente').classList.add('active');
}

function cerrarModalCliente() {
    document.getElementById('modal-cliente').classList.remove('active');
    document.getElementById('form-cliente').reset();
}

document.getElementById('form-cliente')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('cli-id').value;
    const data = {
        id: id,
        nombre: document.getElementById('cli-nombre').value,
        correo: document.getElementById('cli-correo').value,
        telefono: document.getElementById('cli-telefono').value,
        apellido_p: document.getElementById('cli-apellidop').value,
        apellido_m: document.getElementById('cli-apellidom').value
    };

    const metodo = modoEdicionCliente ? 'PUT' : 'POST';
    const endpoint = modoEdicionCliente ? `/clientes/${id}` : '/clientes';

    try {
        const res = await fetch(`${API_URL}${endpoint}`, {
            method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Error al guardar cliente.");
        cerrarModalCliente();
        cargarClientes();
    } catch (error) { alert(error.message); }
});

async function eliminarCliente(id) {
    if (!confirm(`¿Eliminar al cliente ${id}?`)) return;
    try {
        const res = await fetch(`${API_URL}/clientes/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error("No se pudo eliminar (verifica si tiene préstamos activos).");
        cargarClientes();
    } catch (error) { alert(error.message); }
}

// ==========================================
// LÓGICA DE CATEGORÍAS
// ==========================================
let modoEdicionCat = false;

async function cargarCategorias() {
    const tbody = document.getElementById('tabla-categorias');
    if (!tbody) return;
    try {
        const categorias = await obtenerDatos('/categorias');
        tbody.innerHTML = '';
        categorias.forEach(c => {
            tbody.innerHTML += `
                <tr>
                    <td><strong>${c.id}</strong></td>
                    <td>${c.nombre}</td>
                    <td>
                        <button class="btn-edit" onclick="abrirModalCat('editar', '${c.id}', '${c.nombre}')">Editar</button>
                        <button class="btn-danger" onclick="eliminarCategoria('${c.id}')">Eliminar</button>
                    </td>
                </tr>`;
        });
    } catch (error) { tbody.innerHTML = `<tr><td colspan="3" class="mensaje-error">Error: ${error.message}</td></tr>`; }
}

function abrirModalCat(modo, id='', nombre='') {
    modoEdicionCat = (modo === 'editar');
    document.getElementById('modal-cat-titulo').innerText = modoEdicionCat ? 'Editar Categoría' : 'Nueva Categoría';
    document.getElementById('cat-id').value = id;
    document.getElementById('cat-id').disabled = modoEdicionCat;
    document.getElementById('cat-nombre').value = nombre;
    document.getElementById('modal-categoria').classList.add('active');
}

function cerrarModalCat() {
    document.getElementById('modal-categoria').classList.remove('active');
    document.getElementById('form-categoria').reset();
}

document.getElementById('form-categoria')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('cat-id').value;
    const data = { id: id, nombre: document.getElementById('cat-nombre').value };
    const endpoint = modoEdicionCat ? `/categorias/${id}` : '/categorias';
    try {
        const res = await fetch(`${API_URL}${endpoint}`, {
            method: modoEdicionCat ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Error al guardar la categoría.");
        cerrarModalCat();
        cargarCategorias();
    } catch (error) { alert(error.message); }
});

async function eliminarCategoria(id) {
    if (!confirm(`¿Eliminar la categoría ${id}?`)) return;
    try {
        const res = await fetch(`${API_URL}/categorias/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error("No se pudo eliminar (puede que esté asignada a un libro).");
        cargarCategorias();
    } catch (error) { alert(error.message); }
}

// ==========================================
// RUTEO SEGURO (Basado en elementos HTML)
// ==========================================
if (document.getElementById('tabla-dashboard-prestamos')) cargarDashboard();
if (document.getElementById('tabla-libros')) cargarLibros();
if (document.getElementById('tabla-prestamos')) cargarPrestamos();
if (document.getElementById('tabla-usuarios')) cargarUsuarios();
if (document.getElementById('tabla-clientes')) cargarClientes();
if (document.getElementById('tabla-categorias')) cargarCategorias();
