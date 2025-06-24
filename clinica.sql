-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 25-06-2025 a las 01:11:39
-- Versión del servidor: 10.4.28-MariaDB
-- Versión de PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `clinica`
--
CREATE DATABASE IF NOT EXISTS `clinica` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `clinica`;

DELIMITER $$
--
-- Procedimientos
--
DROP PROCEDURE IF EXISTS `sp_registrar_medico`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_registrar_medico` (IN `p_nombre` VARCHAR(50), IN `p_apellido` VARCHAR(50), IN `p_telefono` VARCHAR(9), IN `p_idespecialidad` INT, IN `p_usuario` VARCHAR(50), IN `p_contrasena` VARCHAR(100))   BEGIN
    DECLARE ultimo_num INT;
    DECLARE cod_usuario VARCHAR(8);
    DECLARE cod_medico VARCHAR(8);

    -- Obtener el último número de CodUsuario
    SELECT IFNULL(MAX(CAST(SUBSTRING(CodUsuario, 2) AS UNSIGNED)), 0)
    INTO ultimo_num FROM Usuario;

    -- Generar códigos automáticos
    SET cod_usuario = CONCAT('U', LPAD(ultimo_num + 1, 7, '0'));
    SET cod_medico  = CONCAT('M', LPAD(ultimo_num + 1, 7, '0'));

    -- Insertar en tabla Usuario (Rol 2 = Médico)
    INSERT INTO Usuario (CodUsuario, Usuario, Contraseña, IdRol)
    VALUES (cod_usuario, p_usuario, p_contrasena, 2);

    -- Insertar en tabla Medico
    INSERT INTO Medico (CodMedico, Nombre, Apellido, Telefono, IdEspecialidad, CodUsuario)
    VALUES (cod_medico, p_nombre, p_apellido, p_telefono, p_idespecialidad, cod_usuario);
END$$

DROP PROCEDURE IF EXISTS `sp_registrar_paciente`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_registrar_paciente` (IN `p_nombre` VARCHAR(50), IN `p_apellido` VARCHAR(50), IN `p_edad` INT, IN `p_dui` VARCHAR(10), IN `p_direccion` VARCHAR(100), IN `p_telefono` VARCHAR(9), IN `p_usuario` VARCHAR(50), IN `p_contrasena` VARCHAR(50))   BEGIN
    DECLARE nuevo_cod_usuario VARCHAR(8);
    DECLARE nuevo_cod_expediente VARCHAR(8);
    DECLARE ultimo_num INT;

    -- Paso 1: Obtener el último número de CodUsuario (U0000123 → 123)
    SELECT IFNULL(MAX(CAST(SUBSTRING(CodUsuario, 2) AS UNSIGNED)), 0)
    INTO ultimo_num FROM Usuario;

    -- Paso 2: Generar nuevo código (U0000124)
    SET nuevo_cod_usuario = CONCAT('U', LPAD(ultimo_num + 1, 7, '0'));
    SET nuevo_cod_expediente = CONCAT('P', LPAD(ultimo_num + 1, 7, '0'));

    -- Paso 3: Insertar en tabla Usuario
    INSERT INTO Usuario (CodUsuario, Usuario, Contraseña, IdRol)
    VALUES (nuevo_cod_usuario, p_usuario, p_contrasena, 3);

    -- Paso 4: Insertar en tabla Paciente
    INSERT INTO Paciente (CodExpediente, Nombre, Apellido, Edad, DUI, Direccion, Telefono, CodUsuario)
    VALUES (nuevo_cod_expediente, p_nombre, p_apellido, p_edad, p_dui, p_direccion, p_telefono, nuevo_cod_usuario);
END$$

--
-- Funciones
--
DROP FUNCTION IF EXISTS `ObtenerSiguienteCodCita`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `ObtenerSiguienteCodCita` () RETURNS VARCHAR(8) CHARSET utf8mb4 COLLATE utf8mb4_general_ci  BEGIN
    DECLARE nuevo_codigo VARCHAR(8);
    DECLARE ultimo_codigo VARCHAR(8);
    DECLARE numero INT;

    SELECT CodCita INTO ultimo_codigo
    FROM Cita
    ORDER BY CodCita DESC
    LIMIT 1;

    IF ultimo_codigo IS NULL THEN
        SET nuevo_codigo = 'C0000001';
    ELSE
        SET numero = CAST(SUBSTRING(ultimo_codigo, 2) AS UNSIGNED) + 1;
        SET nuevo_codigo = CONCAT('C', LPAD(numero, 7, '0'));
    END IF;

    RETURN nuevo_codigo;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cita`
--

DROP TABLE IF EXISTS `cita`;
CREATE TABLE IF NOT EXISTS `cita` (
  `CodCita` varchar(8) NOT NULL,
  `FechaCita` date DEFAULT NULL,
  `HoraCita` time DEFAULT NULL,
  `Motivo` varchar(50) DEFAULT NULL,
  `CodExpediente` varchar(8) DEFAULT NULL,
  `CodMedico` varchar(8) DEFAULT NULL,
  `IdEstado` int(11) DEFAULT NULL,
  PRIMARY KEY (`CodCita`),
  KEY `CodExpediente` (`CodExpediente`),
  KEY `CodMedico` (`CodMedico`),
  KEY `fk_estado_cita` (`IdEstado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELACIONES PARA LA TABLA `cita`:
--   `CodExpediente`
--       `paciente` -> `CodExpediente`
--   `CodMedico`
--       `medico` -> `CodMedico`
--   `IdEstado`
--       `estadocita` -> `IdEstado`
--

--
-- Volcado de datos para la tabla `cita`
--

INSERT INTO `cita` (`CodCita`, `FechaCita`, `HoraCita`, `Motivo`, `CodExpediente`, `CodMedico`, `IdEstado`) VALUES
('C0000001', '2025-06-25', '10:00:00', 'Consulta General', 'P0000016', 'M0000003', 3),
('C0000002', '2025-06-27', '13:00:00', 'Consulta General', 'P0000019', 'M0000003', 3),
('C0000003', '2025-06-21', '13:00:00', 'Consulta General', 'P0000018', 'M0000002', 4),
('C0000004', '2025-06-25', '08:30:00', 'Consulta general', 'P0000011', 'M0000001', 1),
('C0000005', '2025-06-26', '10:00:00', 'Dolor de cabeza', 'P0000012', 'M0000002', 4),
('C0000006', '2025-06-27', '11:30:00', 'Control de presión', 'P0000013', 'M0000001', 2),
('C0000007', '2025-06-28', '09:00:00', 'Revisión postoperatoria', 'P0000014', 'M0000003', 1),
('C0000008', '2025-06-29', '14:00:00', 'Consulta pediátrica', 'P0000015', 'M0000002', 3),
('C0000009', '2025-06-30', '15:30:00', 'Chequeo anual', 'P0000016', 'M0000004', 1),
('C0000010', '2025-07-01', '13:00:00', 'Dolor de espalda', 'P0000017', 'M0000005', 1),
('C0000011', '2025-07-02', '10:30:00', 'Consulta dermatológica', 'P0000018', 'M0000006', 1),
('C0000012', '2025-07-03', '09:00:00', 'Control diabetes', 'P0000019', 'M0000007', 2),
('C0000013', '2025-07-04', '11:00:00', 'Consulta general', 'P0000020', 'M0000008', 1),
('C0000014', '2025-06-21', '13:30:00', 'Consulta General', 'P0000012', 'M0000002', 4),
('C0000015', '2025-06-22', '10:00:00', 'Consulta General', 'P0000023', 'M0000003', 1);

--
-- Disparadores `cita`
--
DROP TRIGGER IF EXISTS `before_insert_cita`;
DELIMITER $$
CREATE TRIGGER `before_insert_cita` BEFORE INSERT ON `cita` FOR EACH ROW BEGIN
    IF NEW.CodCita IS NULL OR NEW.CodCita = '' THEN
        SET NEW.CodCita = ObtenerSiguienteCodCita();
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `especialidad`
--

DROP TABLE IF EXISTS `especialidad`;
CREATE TABLE IF NOT EXISTS `especialidad` (
  `IdEspecialidad` int(11) NOT NULL,
  `Especialidad` varchar(50) NOT NULL,
  PRIMARY KEY (`IdEspecialidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELACIONES PARA LA TABLA `especialidad`:
--

--
-- Volcado de datos para la tabla `especialidad`
--

INSERT INTO `especialidad` (`IdEspecialidad`, `Especialidad`) VALUES
(1, 'Cardiología'),
(2, 'Pediatría'),
(3, 'Dermatología'),
(4, 'Neurología'),
(5, 'Ginecología'),
(6, 'Medicina General'),
(7, 'Ortopedia'),
(8, 'Oftalmología'),
(9, 'Psiquiatría'),
(10, 'Endocrinología');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estadocita`
--

DROP TABLE IF EXISTS `estadocita`;
CREATE TABLE IF NOT EXISTS `estadocita` (
  `IdEstado` int(11) NOT NULL AUTO_INCREMENT,
  `NombreEstado` varchar(20) NOT NULL,
  PRIMARY KEY (`IdEstado`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELACIONES PARA LA TABLA `estadocita`:
--

--
-- Volcado de datos para la tabla `estadocita`
--

INSERT INTO `estadocita` (`IdEstado`, `NombreEstado`) VALUES
(1, 'Pendiente'),
(2, 'Reprogramada'),
(3, 'Cancelada'),
(4, 'Completada');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historialclinico`
--

DROP TABLE IF EXISTS `historialclinico`;
CREATE TABLE IF NOT EXISTS `historialclinico` (
  `CodConsulta` varchar(10) NOT NULL,
  `CodExpediente` varchar(8) DEFAULT NULL,
  `MotivoConsulta` varchar(500) DEFAULT NULL,
  `Diagnostico` varchar(500) DEFAULT NULL,
  `FechaConsulta` date DEFAULT NULL,
  `CodMedico` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`CodConsulta`),
  KEY `CodMedico` (`CodMedico`),
  KEY `CodExpediente` (`CodExpediente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELACIONES PARA LA TABLA `historialclinico`:
--   `CodMedico`
--       `medico` -> `CodMedico`
--   `CodExpediente`
--       `paciente` -> `CodExpediente`
--

--
-- Volcado de datos para la tabla `historialclinico`
--

INSERT INTO `historialclinico` (`CodConsulta`, `CodExpediente`, `MotivoConsulta`, `Diagnostico`, `FechaConsulta`, `CodMedico`) VALUES
('CON00001', 'P0000018', 'Consulta General', 'Virus respiratorio', '2025-06-21', 'M0000002'),
('CON00002', 'P0000012', 'Dolor de cabeza', 'Migraña', '2025-06-26', 'M0000002'),
('CON00003', 'P0000012', 'Consulta General', 'Enfermedad gastrointestinal ', '2025-06-21', 'M0000002');

--
-- Disparadores `historialclinico`
--
DROP TRIGGER IF EXISTS `trg_cod_consulta`;
DELIMITER $$
CREATE TRIGGER `trg_cod_consulta` BEFORE INSERT ON `historialclinico` FOR EACH ROW BEGIN
    DECLARE ultimo_codigo VARCHAR(10);
    DECLARE ultimo_num INT;

    -- Obtener el último código (máximo alfanumérico)
    SELECT CodConsulta
    INTO ultimo_codigo
    FROM historialclinico
    ORDER BY CodConsulta DESC
    LIMIT 1;

    -- Si no hay registros previos, comenzamos desde 1
    IF ultimo_codigo IS NULL THEN
        SET ultimo_num = 1;
    ELSE
        -- Extraer la parte numérica y convertir a entero
        SET ultimo_num = CAST(SUBSTRING(ultimo_codigo, 4) AS UNSIGNED) + 1;
    END IF;

    -- Formar el nuevo código, ej: CON00012
    SET NEW.CodConsulta = CONCAT('CON', LPAD(ultimo_num, 5, '0'));
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `horariomedico`
--

DROP TABLE IF EXISTS `horariomedico`;
CREATE TABLE IF NOT EXISTS `horariomedico` (
  `IdHorario` int(11) NOT NULL AUTO_INCREMENT,
  `CodMedico` varchar(8) DEFAULT NULL,
  `DiaSemana` enum('Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo') DEFAULT NULL,
  `HoraInicio` time DEFAULT NULL,
  `HoraFin` time DEFAULT NULL,
  PRIMARY KEY (`IdHorario`),
  KEY `CodMedico` (`CodMedico`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELACIONES PARA LA TABLA `horariomedico`:
--   `CodMedico`
--       `medico` -> `CodMedico`
--

--
-- Volcado de datos para la tabla `horariomedico`
--

INSERT INTO `horariomedico` (`IdHorario`, `CodMedico`, `DiaSemana`, `HoraInicio`, `HoraFin`) VALUES
(1, 'M0000001', 'Lunes', '08:00:00', '12:00:00'),
(2, 'M0000001', 'Martes', '08:00:00', '12:00:00'),
(3, 'M0000001', 'Miércoles', '08:00:00', '12:00:00'),
(4, 'M0000001', 'Jueves', '08:00:00', '12:00:00'),
(5, 'M0000001', 'Viernes', '08:00:00', '12:00:00'),
(6, 'M0000002', 'Lunes', '13:00:00', '17:00:00'),
(7, 'M0000002', 'Martes', '13:00:00', '17:00:00'),
(8, 'M0000002', 'Miércoles', '13:00:00', '17:00:00'),
(9, 'M0000002', 'Jueves', '13:00:00', '17:00:00'),
(10, 'M0000002', 'Viernes', '13:00:00', '17:00:00'),
(11, 'M0000002', 'Sábado', '13:00:00', '17:00:00'),
(12, 'M0000003', 'Lunes', '09:00:00', '15:00:00'),
(13, 'M0000003', 'Martes', '09:00:00', '15:00:00'),
(14, 'M0000003', 'Miércoles', '09:00:00', '15:00:00'),
(15, 'M0000003', 'Jueves', '09:00:00', '15:00:00'),
(16, 'M0000003', 'Viernes', '09:00:00', '15:00:00'),
(17, 'M0000003', 'Sábado', '10:00:00', '14:00:00'),
(18, 'M0000003', 'Domingo', '10:00:00', '14:00:00');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `medico`
--

DROP TABLE IF EXISTS `medico`;
CREATE TABLE IF NOT EXISTS `medico` (
  `CodMedico` varchar(8) NOT NULL,
  `Nombre` varchar(50) DEFAULT NULL,
  `Apellido` varchar(50) DEFAULT NULL,
  `Telefono` varchar(9) DEFAULT NULL,
  `IdEspecialidad` int(11) DEFAULT NULL,
  `CodUsuario` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`CodMedico`),
  KEY `IdEspecialidad` (`IdEspecialidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELACIONES PARA LA TABLA `medico`:
--   `IdEspecialidad`
--       `especialidad` -> `IdEspecialidad`
--

--
-- Volcado de datos para la tabla `medico`
--

INSERT INTO `medico` (`CodMedico`, `Nombre`, `Apellido`, `Telefono`, `IdEspecialidad`, `CodUsuario`) VALUES
('M0000001', 'Juan', 'Pérez', '7001-1223', 1, 'U0000001'),
('M0000002', 'María', 'López', '7002-2334', 2, 'U0000002'),
('M0000003', 'Carlos', 'Gómez', '7003-3445', 3, 'U0000003'),
('M0000004', 'Ana', 'Ramírez', '7004-4556', 4, 'U0000004'),
('M0000005', 'Luis', 'Martínez', '7005-5667', 5, 'U0000005'),
('M0000006', 'Sofía', 'Hernández', '7006-6778', 6, 'U0000006'),
('M0000007', 'Pedro', 'Vargas', '7007-7889', 7, 'U0000007'),
('M0000008', 'Lucía', 'Castillo', '7008-8990', 8, 'U0000008'),
('M0000009', 'Miguel', 'Torres', '7009-9001', 9, 'U0000009'),
('M0000010', 'Elena', 'Santos', '7010-0112', 10, 'U0000010'),
('M0000024', 'Carmen', 'Campos', '8956-7856', 3, 'U0000024');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `paciente`
--

DROP TABLE IF EXISTS `paciente`;
CREATE TABLE IF NOT EXISTS `paciente` (
  `CodExpediente` varchar(8) NOT NULL,
  `Nombre` varchar(50) NOT NULL,
  `Apellido` varchar(50) NOT NULL,
  `Edad` int(11) NOT NULL,
  `DUI` varchar(10) DEFAULT NULL,
  `Direccion` varchar(100) NOT NULL,
  `Telefono` varchar(9) NOT NULL,
  `CodUsuario` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`CodExpediente`),
  KEY `CodUsuario` (`CodUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELACIONES PARA LA TABLA `paciente`:
--   `CodUsuario`
--       `usuario` -> `CodUsuario`
--

--
-- Volcado de datos para la tabla `paciente`
--

INSERT INTO `paciente` (`CodExpediente`, `Nombre`, `Apellido`, `Edad`, `DUI`, `Direccion`, `Telefono`, `CodUsuario`) VALUES
('P0000011', 'José', 'Martínez', 35, '01234567-8', 'Av. Principal #123', '70011223', 'U0000011'),
('P0000012', 'Ana', 'Gómez', 28, '02345678-9', 'Calle Secundaria #45', '70022334', 'U0000012'),
('P0000013', 'Carlos', 'Pérez', 42, '03456789-0', 'Col. Las Flores #67', '70033445', 'U0000013'),
('P0000014', 'Laura', 'Ramírez', 30, '04567890-1', 'Residencial El Sol', '70044556', 'U0000014'),
('P0000015', 'Luis', 'Sánchez', 50, '05678901-2', 'Barrio Central #89', '70055667', 'U0000015'),
('P0000016', 'María', 'Lopez', 15, NULL, 'Col. La Paz #10', '70066778', 'U0000016'),
('P0000017', 'Pedro', 'Vargas', 12, NULL, 'Av. Reforma #120', '70077889', 'U0000017'),
('P0000018', 'Sofía', 'Castillo', 16, NULL, 'Residencial Los Pinos', '70088990', 'U0000018'),
('P0000019', 'Diego', 'Torres', 14, NULL, 'Barrio San Juan', '70099001', 'U0000019'),
('P0000020', 'Elena', 'Santos', 17, NULL, 'Col. Las Palmas #23', '70100112', 'U0000020'),
('P0000023', 'Marcela', 'Martinez ', 20, '98785697-8', 'San Salvador', '8956-8956', 'U0000023');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

DROP TABLE IF EXISTS `roles`;
CREATE TABLE IF NOT EXISTS `roles` (
  `IdRol` int(11) NOT NULL,
  `Rol` varchar(40) NOT NULL,
  PRIMARY KEY (`IdRol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELACIONES PARA LA TABLA `roles`:
--

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`IdRol`, `Rol`) VALUES
(1, 'Administrador'),
(2, 'Médico'),
(3, 'Paciente'),
(4, 'Recepcionista');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

DROP TABLE IF EXISTS `usuario`;
CREATE TABLE IF NOT EXISTS `usuario` (
  `CodUsuario` varchar(8) NOT NULL,
  `Usuario` varchar(50) DEFAULT NULL,
  `Contraseña` varchar(50) DEFAULT NULL,
  `IdRol` int(11) DEFAULT NULL,
  PRIMARY KEY (`CodUsuario`),
  KEY `IdRol` (`IdRol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELACIONES PARA LA TABLA `usuario`:
--   `IdRol`
--       `roles` -> `IdRol`
--

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`CodUsuario`, `Usuario`, `Contraseña`, `IdRol`) VALUES
('U0000001', 'juanperez', 'pass1234', 2),
('U0000002', 'marialopez', 'pass2345', 2),
('U0000003', 'carlosgomez', 'carlosgomez', 2),
('U0000004', 'anaramirez', 'pass4567', 2),
('U0000005', 'luismartinez', 'pass5678', 2),
('U0000006', 'sofiahdez', 'pass6789', 2),
('U0000007', 'pedrovargas', 'pass7890', 2),
('U0000008', 'luciacastillo', 'pass8901', 2),
('U0000009', 'migueltorres', 'pass9012', 2),
('U0000010', 'elenasantos', 'pass0123', 2),
('U0000011', 'josemart', 'pass1234', 3),
('U0000012', 'anagomez', 'pass2345', 3),
('U0000013', 'carlosp', 'pass3456', 3),
('U0000014', 'lauraram', 'pass4567', 3),
('U0000015', 'luiss', 'pass5678', 3),
('U0000016', 'marial', 'pass6789', 3),
('U0000017', 'pedrov', 'pass7890', 3),
('U0000018', 'sofiac', 'pass8901', 3),
('U0000019', 'diegot', 'pass9012', 3),
('U0000020', 'elenas', 'pass0123', 3),
('U0000021', 'admin1', 'admin123', 1),
('U0000022', 'recepcion1', 'recep123', 4),
('U0000023', 'Martorr', '123456', 3),
('U0000024', 'Carcam', '12345', 2);

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `cita`
--
ALTER TABLE `cita`
  ADD CONSTRAINT `cita_ibfk_1` FOREIGN KEY (`CodExpediente`) REFERENCES `paciente` (`CodExpediente`),
  ADD CONSTRAINT `cita_ibfk_2` FOREIGN KEY (`CodMedico`) REFERENCES `medico` (`CodMedico`),
  ADD CONSTRAINT `fk_estado_cita` FOREIGN KEY (`IdEstado`) REFERENCES `estadocita` (`IdEstado`);

--
-- Filtros para la tabla `historialclinico`
--
ALTER TABLE `historialclinico`
  ADD CONSTRAINT `historialclinico_ibfk_1` FOREIGN KEY (`CodMedico`) REFERENCES `medico` (`CodMedico`),
  ADD CONSTRAINT `historialclinico_ibfk_2` FOREIGN KEY (`CodExpediente`) REFERENCES `paciente` (`CodExpediente`);

--
-- Filtros para la tabla `horariomedico`
--
ALTER TABLE `horariomedico`
  ADD CONSTRAINT `horariomedico_ibfk_1` FOREIGN KEY (`CodMedico`) REFERENCES `medico` (`CodMedico`);

--
-- Filtros para la tabla `medico`
--
ALTER TABLE `medico`
  ADD CONSTRAINT `medico_ibfk_1` FOREIGN KEY (`IdEspecialidad`) REFERENCES `especialidad` (`IdEspecialidad`);

--
-- Filtros para la tabla `paciente`
--
ALTER TABLE `paciente`
  ADD CONSTRAINT `paciente_ibfk_1` FOREIGN KEY (`CodUsuario`) REFERENCES `usuario` (`CodUsuario`);

--
-- Filtros para la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`IdRol`) REFERENCES `roles` (`IdRol`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
