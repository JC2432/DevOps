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

// Ejecutar funciones dependiendo de la página en la que estemos
if (window.location.pathname.includes('libros.html')) {
    cargarLibros();
}
