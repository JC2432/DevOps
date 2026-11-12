-- Datos de ejemplo
-- El orden importa: primero los catálogos, luego las tablas que los referencian (FK).

INSERT INTO NACIONALIDAD (NACIONALIDAD_ID, NOMBRE) VALUES
('N001', 'Mexicana'), ('N002', 'Española'), ('N003', 'Estadounidense');

INSERT INTO AUTORES (AUTOR_ID, NACIONALIDAD_ID, NOMBRE_AUTOR, APELLIDO_P, APELLIDO_M) VALUES
('A001', 'N001', 'Juan', 'Rulfo', NULL);

INSERT INTO EDITORIAL (EDITORIAL_ID, NOMBRE) VALUES
('E001', 'Fondo de Cultura Económica'), ('E002', 'Planeta');

INSERT INTO CATEGORIAS (CATEGORIA_ID, NOMBRE_CATEGORIA) VALUES
('C001', 'Ciencia Ficción'), ('C002', 'Historia'), ('C003', 'Tecnología');

INSERT INTO CARGO (CARGO_ID, PUESTO) VALUES
('R001', 'ADMINISTRADOR'), ('R002', 'BIBLIOTECARIO');

INSERT INTO ESTADO_PRESTAMOS (ESTADO_PRESTAMOS_ID, ESTADO) VALUES
('S001', 'ACTIVO'), ('S002', 'DEVUELTO'), ('S003', 'VENCIDO');

-- Usuario de prueba. La contraseña es un placeholder (no sirve para iniciar sesión);
-- los usuarios creados por la API sí guardan la contraseña hasheada.
INSERT INTO USUARIOS (USUARIO_ID, CARGO_ID, USERNAME, PASSWORD, NOMBRE, APELLIDO_P) VALUES
('U001', 'R001', 'admin_db', 'placeholder-sin-login', 'Juan', 'Pérez');

INSERT INTO CLIENTES (CLIENTE_ID, NOMBRE, APELLIDO_P, APELLIDO_M, CORREO, TELEFONO) VALUES
('C001', 'Ana', 'López', NULL, 'ana@example.com', NULL);

INSERT INTO LIBROS (LIBRO_ID, EDITORIAL_ID, TITULO, ANIO_PUBLICACION, DISPONIBLE) VALUES
('L001', 'E001', 'Introducción a Bases de Datos', 2023, 1);
