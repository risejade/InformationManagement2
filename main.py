from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from os import getenv

app = Flask(__name__)

load_dotenv()

# Get environment variables
MYSQL_HOST = getenv("MYSQL_HOST")
MYSQL_USER = getenv("MYSQL_USER")
MYSQL_PASSWORD = getenv("MYSQL_PASSWORD")
MYSQL_DB = getenv("MYSQL_DB")
MYSQL_CURSORCLASS = getenv("MYSQL_CURSORCLASS")
MYSQL_AUTOCOMMIT = True if getenv("MYSQL_AUTOCOMMIT") == "True" else False

# MySQL connection setup
app.config["MYSQL_HOST"] = MYSQL_HOST
app.config["MYSQL_USER"] = MYSQL_USER
app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DB"] = MYSQL_DB
app.config["MYSQL_CURSORCLASS"] = MYSQL_CURSORCLASS
app.config["MYSQL_AUTOCOMMIT"] = MYSQL_AUTOCOMMIT

mysql = MySQL(app)

# Function to execute queries
def execute_query(query, data=None):
    msg = ""
    cursor = None
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute(query, data)
        
        # Fetch all results if the query is a SELECT query
        if cursor.with_rows:
            result = cursor.fetchall()
        else:
            result = None

        if MYSQL_AUTOCOMMIT:
            mysql.connection.commit()

        msg = {"message": "Query executed successfully", "result": result}
    except mysql.connector.Error as err:
        msg = {"error": f"Failed to execute query: {err}"}
    finally:
        if cursor:
            cursor.close()
        return msg

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_student")
def add_student():
    return render_template("add_student.html")

@app.route("/submit_student", methods=["POST"])
def submit_student():
    if request.method == "POST":
        student_name = request.form["student_name"]
        date_of_birth = request.form["date_of_birth"]
        address = request.form["address"]
        email = request.form["email"]
        phone_number = request.form["phone_number"]

        query = "INSERT INTO Students (student_name, date_of_birth, address, email, phone_number) VALUES (%s, %s, %s, %s, %s)"
        data = (student_name, date_of_birth, address, email, phone_number)

        msg = execute_query(query, data)

        return render_template("success_record.html", msg=msg)
    else:
        return "Method Not Allowed", 405

@app.route("/student_info")
def student_info():
    query = "SELECT * FROM Students"
    
    cursor = None
    students = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        students = cursor.fetchall()
    except mysql.connector.Error as err:
        msg = f"Failed to fetch student records: {err}"
        return render_template("success_record.html", msg=msg)
    finally:
        if cursor:
            cursor.close()

    return render_template("student_info.html", students=students)


@app.route("/courses", methods=["POST"])
def add_course():
    if request.method == "POST":
        data = request.get_json()
        try:
            course_name = data["course_name"]
            course_description = data.get("course_description", "")

            if course_name:
                cursor = mysql.cursor()
                cursor.execute(
                    "INSERT INTO Courses (course_name, course_description) VALUES (%s, %s)",
                    (course_name, course_description)
                )
                mysql.commit()
                result = {"message": "Course created successfully"}
            else:
                result = {"error": "Course name is required"}
        except mysql.connector.Error as err:
            result = {"error": f"Failed to create course: {err}"}
        finally:
            cursor.close()
        return jsonify(result)


@app.route("/programs", methods=["POST"])
def add_program():
    if request.method == "POST":
        data = request.get_json()
        try:
            program_name = data["program_name"]
            program_description = data.get("program_description", "")

            if program_name:
                cursor = mysql.cursor()
                cursor.execute(
                    "INSERT INTO Programs (program_name, program_description) VALUES (%s, %s)",
                    (program_name, program_description)
                )
                mysql.commit()
                result = {"message": "Program created successfully"}
            else:
                result = {"error": "Program name is required"}
        except mysql.connector.Error as err:
            result = {"error": f"Failed to create program: {err}"}
        finally:
            cursor.close()
        return jsonify(result)


@app.route("/enrollment", methods=["POST"])
def add_enrollment():
    if request.method == "POST":
        data = request.get_json()
        try:
            student_id = data.get("student_id")
            course_id = data.get("course_id")

            if student_id and course_id:
                cursor = mysql.cursor()
                cursor.execute(
                    "INSERT INTO Enrollment (student_id, course_id) VALUES (%s, %s)",
                    (student_id, course_id)
                )
                mysql.commit()
                result = {"message": "Enrollment created successfully"}
            else:
                result = {"error": "Both student_id and course_id are required"}
        except mysql.connector.Error as err:
            result = {"error": f"Failed to create enrollment: {err}"}
        finally:
            cursor.close()
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)