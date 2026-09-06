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
    
    // Estado de carga
    contenedor.innerHTML = '<div class="mensaje-cargando">Cargando libros...</div>';

    try {
        const libros = await obtenerDatos('/libros');
        
        // Construcción de la tabla
        let htmlTabla = `
            <h2>Lista de Libros</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Título</th>
                        <th>Año</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
        `;

        libros.forEach(libro => {
            htmlTabla += `
                <tr>
                    <td>${libro.id}</td>
                    <td>${libro.titulo}</td>
                    <td>${libro.anio}</td>
                    <td>${libro.disponible ? 'Disponible' : 'Prestado'}</td>
                </tr>
            `;
        });

        htmlTabla += '</tbody></table>';
        contenedor.innerHTML = htmlTabla;

    } catch (error) {
        // Estado de error visual para el usuario
        contenedor.innerHTML = `
            <div class="mensaje-error">
                No se pudo cargar la lista de libros. Verifica que el backend esté encendido en http://localhost:8000.<br>
                Detalle: ${error.message}
            </div>
        `;
    }
}

// Función para renderizar préstamos
async function cargarPrestamos() {
    const contenedor = document.getElementById('contenedor-principal');
    contenedor.innerHTML = '<div class="mensaje-cargando">Cargando préstamos...</div>';

    try {
        const prestamos = await obtenerDatos('/prestamos');
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
                    <td>${p.id}</td>
                    <td>${p.cliente}</td>
                    <td>${p.fecha_prestamo}</td>
                    <td>${p.estado}</td>
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
        const usuarios = await obtenerDatos('/usuarios');
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
                    <td>${u.username}</td>
                    <td>${u.nombre} ${u.apellido_p}</td>
                    <td>${u.cargo}</td>
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
