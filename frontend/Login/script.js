const API_URL = 'http://localhost:8000';
const SESSION_KEY = 'usuario';

// Si ya hay sesión, ir directo al dashboard
if (sessionStorage.getItem(SESSION_KEY)) {
    window.location.replace('../index.html');
}

document.getElementById('loginForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const cargo = document.getElementById('role').value;
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
        sessionStorage.setItem(SESSION_KEY, JSON.stringify(usuario));
        window.location.href = '../index.html';
    } catch (e) {
        errorMessage.textContent = 'No se pudo conectar con el servidor. ¿Está corriendo el backend?';
    } finally {
        boton.disabled = false;
    }
});
