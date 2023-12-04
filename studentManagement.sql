USE dbStudentManagementSystem;

-- Create Students table
CREATE TABLE Students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    address VARCHAR(255),
    email VARCHAR(100),
    phone_number VARCHAR(20)
);

-- Create Courses table
CREATE TABLE Courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    course_description TEXT
);

-- Create Programs table
CREATE TABLE Programs (
    program_id INT AUTO_INCREMENT PRIMARY KEY,
    program_name VARCHAR(100) NOT NULL,
    program_description TEXT
);

-- Create Enrollment table to assign students to courses
CREATE TABLE Enrollment (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    course_id INT,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

-- Create RecordProgram table to record programs a student is enrolled in
CREATE TABLE RecordProgram (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    program_id INT,
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (program_id) REFERENCES Programs(program_id)
);
