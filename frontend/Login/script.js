// Login. Usa obtenerSesion/guardarSesion/irA/paginaInicio de ../sesion.js

// Si ya hay sesión, ir directo a su página (panel del personal o portal del cliente)
const sesionPrevia = obtenerSesion();
if (sesionPrevia && sesionPrevia.token) {
    irA(paginaInicio(sesionPrevia));
}

// Los clientes entran con su correo; el personal con su nombre de usuario
const selectorPerfil = document.getElementById('role');
function actualizarEtiqueta() {
    const esCliente = selectorPerfil.value === 'CLIENTE';
    document.getElementById('usernameLabel').textContent = esCliente ? 'Correo' : 'Usuario';
    document.getElementById('username').placeholder = esCliente
        ? 'Ingresa tu correo' : 'Ingresa tu usuario';
}
selectorPerfil.addEventListener('change', actualizarEtiqueta);
actualizarEtiqueta();

document.getElementById('loginForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const cargo = selectorPerfil.value;
    const errorMessage = document.getElementById('errorMessage');
    const boton = document.getElementById('loginBtn');

    errorMessage.textContent = '';
    boton.disabled = true;

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, cargo }),
        });

        if (res.status === 401) {
            errorMessage.textContent = 'Usuario, contraseña o perfil incorrectos.';
            return;
        }
        if (!res.ok) {
            errorMessage.textContent = `Error del servidor (${res.status}).`;
            return;
        }

        const usuario = await res.json();
        guardarSesion(usuario);
        irA(paginaInicio(usuario));
    } catch (e) {
        errorMessage.textContent = 'No se pudo conectar con el servidor. ¿Está corriendo el backend?';
    } finally {
        boton.disabled = false;
    }
});
