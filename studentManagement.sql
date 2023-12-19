USE dbStudentManagementSystem;

-- Create Students table
CREATE TABLE Students (
    `student_id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_name` VARCHAR(100) NOT NULL DEFAULT '',
    `birth_date` DATE NOT NULL DEFAULT '',
    `address` VARCHAR(255) NOT NULL DEFAULT '',
    `institutional_email` VARCHAR(100) NOT NULL DEFAULT '',
    `program` VARCHAR(100) NOT NULL DEFAULT '',
    `year` VARCHAR(20) NOT NULL DEFAULT '',
    `age` INT NOT NULL DEFAULT 0
)ENGINE=InnoDB ;

CREATE TABLE Student_Audit_Log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    action VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);

CREATE TABLE `users` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL DEFAULT '',
  `password` varchar(200) NOT NULL DEFAULT '',
  `email` varchar(200) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB ;

CREATE TABLE `gwa` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `student_name` varchar(100) NOT NULL DEFAULT '',
  `student_gwa` float NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB ;


-- SQL JOIN to retrieve student details along with GWA (Grade Weighted Average)
    CREATE VIEW student_user_info AS
    SELECT s.student_id, s.student_name, s.birth_date, s.address, s.institutional_email, s.program, s.year, g.student_gwa
    FROM Students s
    INNER JOIN gwa g ON s.student_name = g.student_name;


-- Stored Procedure to create a new student
DELIMITER $$
CREATE PROCEDURE create_student(
    IN p_name VARCHAR(100),
    IN p_birth_date DATE,
    IN p_address VARCHAR(255),
    IN p_email VARCHAR(100),
    IN p_program VARCHAR(100),
    IN p_year VARCHAR(20)
)
BEGIN
    INSERT INTO Students (student_name, birth_date, address, institutional_email, program, year)
    VALUES (p_name, p_birth_date, p_address, p_email, p_program, p_year);
END$$
DELIMITER ;

-- Stored Procedure to update a student's information
DELIMITER $$
CREATE PROCEDURE update_student(
    IN p_id INT,
    IN p_name VARCHAR(100),
    IN p_birth_date DATE,
    IN p_address VARCHAR(255),
    IN p_email VARCHAR(100),
    IN p_program VARCHAR(100),
    IN p_year VARCHAR(20)
)
BEGIN
    UPDATE Students
    SET student_name = p_name, birth_date = p_birth_date, address = p_address, institutional_email = p_email, program = p_program, year = p_year
    WHERE student_id = p_id;
END$$
DELIMITER ;

-- Stored Procedure to delete a student
DELIMITER $$
CREATE PROCEDURE delete_student(
    IN p_id INT
)
BEGIN
    DELETE FROM Student_Audit_Log
    WHERE student_id = p_id;

    DELETE FROM Students
    WHERE student_id = p_id;
END$$
DELIMITER ;

-- Trigger to audit student record changes
DELIMITER $$
CREATE TRIGGER student_audit_trigger
AFTER UPDATE ON Students
FOR EACH ROW
BEGIN
    INSERT INTO Student_Audit_Log (student_id, student_name, old_institutional_email, new_institutional_email, date_time)
    VALUES (OLD.student_id, OLD.student_name, OLD.institutional_email, NEW.institutional_email, NOW());
END$$
DELIMITER ;

-- Create the function 'calculate_age'
DELIMITER $$
CREATE FUNCTION calculate_age(birth_date DATE) RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE age INT;
    SET age = YEAR(CURDATE()) - YEAR(birth_date);
    IF MONTH(CURDATE()) < MONTH(birth_date) OR (MONTH(CURDATE()) = MONTH(birth_date) AND DAY(CURDATE()) < DAY(birth_date)) THEN
        SET age = age - 1;
    END IF;
    RETURN age;
END$$
DELIMITER ;

DELIMITER $$$

-- Create the procedure for create gwa
CREATE PROCEDURE create_gwa(
  IN p_student_name varchar(100),
  IN p_student_gwa float
)
BEGIN
  INSERT INTO gwa (student_name, student_gwa)
    VALUES (p_student_name, p_student_gwa);
  SELECT LAST_INSERT_ID() AS id;
END$$$

-- Create the procedure for read gwa
DELIMITER $$

CREATE PROCEDURE read_gwa(
  IN gwa_id INT
)
BEGIN
  SELECT * FROM gwa WHERE id = gwa_id;
END $$

DELIMITER ;

-- Create the procedure for update gwa
CREATE PROCEDURE update_gwa(
  IN p_id INT,
  IN p_student_name varchar(100),
  IN p_student_gwa float
)
BEGIN
  UPDATE gwa
    SET student_name = p_student_name,
        student_gwa = p_student_gwa
    WHERE id = p_id;
  SELECT p_id AS id;
END$$$

-- Create the procedure for delete gwa
CREATE PROCEDURE delete_gwa(
  IN p_id INT
)
BEGIN
  DELETE FROM gwa
  WHERE id = p_id;
  SELECT p_id AS id;
END$$$

DELIMITER ;