SET NAMES utf8mb4;
-- Datos de ejemplo. Ejecutar después de schema.sql (que deja las tablas vacías).
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

-- VENCIDO no se guarda a mano: la API muestra como VENCIDO cualquier préstamo ACTIVO
-- cuya FECHA_LIMITE ya pasó. Se conserva el registro por compatibilidad.
INSERT INTO ESTADO_PRESTAMOS (ESTADO_PRESTAMOS_ID, ESTADO) VALUES
('S001', 'ACTIVO'), ('S002', 'DEVUELTO'), ('S003', 'VENCIDO'), ('S004', 'APARTADO');

-- Personal de prueba (SOLO DESARROLLO). Contraseñas hasheadas con PBKDF2:
--   admin_db   / admin123   (ADMINISTRADOR)
--   biblio_db  / biblio123  (BIBLIOTECARIO)
INSERT INTO USUARIOS (USUARIO_ID, CARGO_ID, USERNAME, PASSWORD, NOMBRE, APELLIDO_P) VALUES
('U001', 'R001', 'admin_db',
 'pbkdf2_sha256$600000$f18723e2fa556a144a3e62e4e29e1415$dc6757df02e82d27ed40e363fc67a05bc1c0484c31110d65bf21d35355f02dc4',
 'Juan', 'Pérez'),
('U002', 'R002', 'biblio_db',
 'pbkdf2_sha256$600000$412b7997bc41e39dd097718a5855a34e$18e456be3d1ce2d13373bb95e065ff0d245a9a8fa44001038eb765096a87a8b6',
 'María', 'Gómez');

-- Clientes de prueba (SOLO DESARROLLO). Entran al portal con su correo:
--   ana@example.com   / cliente123
--   luis@example.com  / cliente123
INSERT INTO CLIENTES (CLIENTE_ID, NOMBRE, APELLIDO_P, APELLIDO_M, CORREO, TELEFONO, PASSWORD) VALUES
('C001', 'Ana', 'López', NULL, 'ana@example.com', NULL,
 'pbkdf2_sha256$600000$daa7f0b6b68cded4d0554058817a0330$230416862b56300ea163afe8f9ee5530661bc0957d02bcaf9c39170b63981878'),
('C002', 'Luis', 'Martínez', 'Soto', 'luis@example.com', '8112345678',
 'pbkdf2_sha256$600000$239c232e9d30e6d52e34af83d886dea5$249ad262fe9e16c3500de7c22846554a415c7f42dba0b2720d0601dc3de55576');

-- L001 queda libre: las pruebas automáticas lo usan para prestar y devolver.
INSERT INTO LIBROS (LIBRO_ID, EDITORIAL_ID, TITULO, ANIO_PUBLICACION, DISPONIBLE) VALUES
('L001', 'E001', 'Introducción a Bases de Datos', 2023, TRUE),
('L002', 'E001', 'Pedro Páramo', 1955, FALSE),
('L003', 'E002', 'El Llano en llamas', 1953, FALSE),
('L004', 'E002', 'Historia mínima de México', 1973, FALSE),
('L005', 'E001', 'Fundamentos de DevOps', 2024, TRUE),
('L006', 'E002', 'Crónicas marcianas', 1950, TRUE);

INSERT INTO AUTORES_has_LIBROS (AUTOR_ID, LIBRO_ID) VALUES ('A001', 'L002'), ('A001', 'L003');

INSERT INTO LIBROS_has_CATEGORIAS (CATEGORIA_ID, LIBRO_ID) VALUES
('C003', 'L001'), ('C002', 'L004'), ('C003', 'L005'), ('C001', 'L006');

-- Préstamos de ejemplo con fechas relativas a hoy, para que el portal siempre muestre
-- uno vigente, uno vencido y uno apartado pendiente de recoger.
INSERT INTO PRESTAMOS
    (PRESTAMO_ID, ESTADO_PRESTAMOS_ID, CLIENTE_ID, USUARIO_ID,
     FECHA_PRESTAMO, FECHA_LIMITE, FECHA_DEVOLUCION) VALUES
('P001', 'S001', 'C001', 'U002', CURDATE() - INTERVAL 5 DAY, CURDATE() + INTERVAL 9 DAY, NULL),
('P002', 'S001', 'C002', 'U002', CURDATE() - INTERVAL 20 DAY, CURDATE() - INTERVAL 6 DAY, NULL),
('P003', 'S004', 'C001', NULL, CURDATE(), CURDATE() + INTERVAL 3 DAY, NULL);

INSERT INTO LIBROS_PRESTADOS (PRESTAMO_ID, LIBRO_ID) VALUES
('P001', 'L002'), ('P002', 'L003'), ('P003', 'L004');
