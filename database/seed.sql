-- Datos de ejemplo — a completar por el encargado de BD

-- Insertar catálogos básicos
INSERT INTO AUTORES (AUTOR_ID, NACIONALIDAD_ID, NOMBRE_AUTOR, APELLIDO_P, APELLIDO_M) VALUES
  ('A001', 'N001', 'Juan', 'Rulfo', NULL);
  
INSERT INTO NACIONALIDAD (NACIONALIDAD_ID, NOMBRE) VALUES 
('N001', 'Mexicana'), ('N002', 'Española'), ('N003', 'Estadounidense');

INSERT INTO EDITORIAL (EDITORIAL_ID, NOMBRE) VALUES 
('E001', 'Fondo de Cultura Económica'), ('E002', 'Planeta');

INSERT INTO CATEGORIAS (CATEGORIA_ID, NOMBRE_CATEGORIA) VALUES 
('C001', 'Ciencia Ficción'), ('C002', 'Historia'), ('C003', 'Tecnología');

INSERT INTO CARGO (CARGO_ID, PUESTO) VALUES 
('R001', 'ADMINISTRADOR'), ('R002', 'BIBLIOTECARIO');

INSERT INTO ESTADO_PRESTAMOS (ESTADO_PRESTAMOS_ID, ESTADO) VALUES 
('S001', 'ACTIVO'), ('S002', 'DEVUELTO'), ('S003', 'VENCIDO');

-- Insertar un usuario administrador (La contraseña debe estar hasheada en un entorno real, aquí usamos un placeholder)
INSERT INTO USUARIOS (USUARIO_ID, CARGO_ID, USERNAME, PASSWORD, NOMBRE, APELLIDO_P) VALUES 
('U001', 'R001', 'admin_db', 'hash_de_contrasena_aqui', 'Juan', 'Pérez');

-- Insertar un libro de prueba
INSERT INTO LIBROS (LIBRO_ID, EDITORIAL_ID, TITULO, ANIO_PUBLICACION, DISPONIBLE) VALUES 
('L001', 'E001', 'Introducción a Bases de Datos', 2023, 1);
