document.getElementById('loginForm').addEventListener('submit', function(event) {
    // Evita que la página se recargue al enviar el formulario
    event.preventDefault(); 

    // Capturar los valores ingresados
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    const role = document.getElementById('role').value;
    const errorMessage = document.getElementById('errorMessage');

    // Limpiar mensajes de error previos
    errorMessage.textContent = '';

    // Lógica para detectar qué perfil está ingresando
    if (role === 'bibliotecario') {
        // Aquí iría la validación real contra una base de datos
        alert(`Ingresando al sistema administrativo.\nBienvenido Bibliotecario: ${user}`);
        // window.location.href = 'panel_bibliotecario.html'; 
    } else if (role === 'usuario') {
        alert(`Ingresando al catálogo.\nBienvenido Usuario: ${user}`);
        // window.location.href = 'inicio_usuario.html';
    }
});