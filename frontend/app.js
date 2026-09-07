// Lógica de consumo de la API — a completar por el encargado de frontend
// Configuración base
const API_URL = 'http://localhost:8000';

// Función genérica para consumir la API con manejo de errores
async function obtenerDatos(endpoint) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`);
        
        // Manejo de errores 400, 404, 500
        if (!response.ok) {
            throw new Error(`Error en el servidor: código ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error("Fallo al conectar con la API:", error);
        throw error;
    }
}

// Función específica para renderizar la tabla de libros
async function cargarLibros() {
    const contenedor = document.getElementById('contenedor-principal');
    contenedor.innerHTML = '<div class="mensaje-cargando">Cargando libros...</div>';

    try {
        const data = await obtenerDatos('/libros/');
        const libros = data.libros; // el objeto viene envuelto en {"libros": [...]}

        let htmlTabla = `
            <h2>Lista de Libros</h2>
            <table>
                <thead>
                    <tr><th>ID</th><th>Título</th><th>Año</th><th>Estado</th></tr>
                </thead>
                <tbody>
        `;

        libros.forEach(libro => {
            htmlTabla += `
                <tr>
                    <td>${libro.LIBRO_ID}</td>
                    <td>${libro.TITULO}</td>
                    <td>${libro.ANIO_PUBLICACION}</td>
                    <td>${libro.DISPONIBLE ? 'Disponible' : 'Prestado'}</td>
                </tr>
            `;
        });

        htmlTabla += '</tbody></table>';
        contenedor.innerHTML = htmlTabla;
    } catch (error) {
        contenedor.innerHTML = `<div class="mensaje-error">No se pudo cargar la lista de libros. Verifica que el backend esté encendido en http://localhost:8000.<br>Detalle: ${error.message}</div>`;
    }
}

// Función para renderizar préstamos
async function cargarPrestamos() {
    const contenedor = document.getElementById('contenedor-principal');
    contenedor.innerHTML = '<div class="mensaje-cargando">Cargando préstamos...</div>';

    try {
        const data = await obtenerDatos('/prestamos');
        const prestamos = data.prestamos; // desempaquetar el objeto

        let htmlTabla = `
            <h2>Lista de Préstamos</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID Préstamo</th>
                        <th>Cliente</th>
                        <th>Fecha Préstamo</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
        `;
        prestamos.forEach(p => {
            htmlTabla += `
                <tr>
                    <td>${p.PRESTAMO_ID}</td>
                    <td>${p.CLIENTE_NOMBRE}</td>
                    <td>${p.FECHA_PRESTAMO}</td>
                    <td>${p.ESTADO_NOMBRE}</td>
                </tr>
            `;
        });
        htmlTabla += '</tbody></table>';
        contenedor.innerHTML = htmlTabla;
    } catch (error) {
        contenedor.innerHTML = `<div class="mensaje-error">Error al cargar préstamos: ${error.message}</div>`;
    }
}

// Función para renderizar usuarios
async function cargarUsuarios() {
    const contenedor = document.getElementById('contenedor-principal');
    contenedor.innerHTML = '<div class="mensaje-cargando">Cargando usuarios...</div>';

    try {
        const data = await obtenerDatos('/usuarios');
        const usuarios = data.usuarios; // desempaquetar el objeto

        let htmlTabla = `
            <h2>Directorio de Usuarios</h2>
            <table>
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Nombre</th>
                        <th>Rol</th>
                    </tr>
                </thead>
                <tbody>
        `;
        usuarios.forEach(u => {
            htmlTabla += `
                <tr>
                    <td>${u.USERNAME}</td>
                    <td>${u.NOMBRE} ${u.APELLIDO_P}</td>
                    <td>${u.CARGO_NOMBRE}</td>
                </tr>
            `;
        });
        htmlTabla += '</tbody></table>';
        contenedor.innerHTML = htmlTabla;
    } catch (error) {
        contenedor.innerHTML = `<div class="mensaje-error">Error al cargar usuarios: ${error.message}</div>`;
    }
}

// Lógica de ruteo simple: detecta en qué página estamos y ejecuta la función correspondiente
const rutaActual = window.location.pathname;

if (rutaActual.includes('libros.html')) {
    cargarLibros();
} else if (rutaActual.includes('prestamos.html')) {
    cargarPrestamos();
} else if (rutaActual.includes('usuarios.html')) {
    cargarUsuarios();
}
