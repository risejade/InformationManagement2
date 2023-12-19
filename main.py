from flask import Flask, render_template, request, session, redirect, jsonify, app, url_for
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from os import getenv
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'Stud3ntM'

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

#Benavente's Work
# Function to execute stored procedures
def execute_procedure(procedure_name, data=None):
    msg = {}
    cursor = None  # Initialize cursor variable

    try:
        with mysql.connection.cursor() as cursor:
            cursor.callproc(procedure_name, data)
            result = cursor.fetchall() if cursor.rowcount > 0 else None  # Fetch result after executing the procedure

        if MYSQL_AUTOCOMMIT:
            mysql.connection.commit()
            msg = {"message": "Query executed successfully", "result": result}

    except Exception as e:
        msg = {"error": f"Failed to execute query: {e}"}
    finally:
        if cursor:
            cursor.close()

    return msg
    

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/add_gwa")
def add_gwa_page():
    return render_template("add_gwa.html")

@app.route("/edit_gwa")
def edit_gwa_page():
    return render_template("edit_gwa.html")

@app.route("/index.html")
def home_page():
    return render_template("index.html")

@app.route("/index")
def index():
    if "username" in session:  # Check if the user is logged in
        return render_template("index.html")
    else:
        return redirect("/")


@app.route("/add_student")
def add_student():
    return render_template("add_student.html")

# Function to calculate the age of a student based on birth date
@app.route("/calculate_age", methods=["GET", "POST"])
def calculate_age():
    if request.method == "POST":
        birth_date = request.form["birth_date"]

        query = "SELECT calculate_age(%s) AS age"
        data = (birth_date,)

        result = execute_procedure(query, data)

        if result.get("result"):
            age = result["result"][0]["age"]
            return render_template("age.html", age=age)
        else:
            return render_template("error.html", error="Failed to calculate age")
    else:
        # Handle GET requests to this route (e.g., display an error or redirect)
        return render_template("error.html", error="Method Not Allowed")
    
# Add Student using Stored Procedure
@app.route("/submit_student", methods=["POST"])
def submit_student():
    if request.method == "POST":
        student_name = request.form["student_name"]
        date_of_birth = request.form["birth_date"]
        address = request.form["address"]
        email = request.form["institutional_email"]
        program = request.form["program"]
        year = request.form["year"]

        # Call the stored procedure to add a student
        procedure_name = "create_student"
        data = (student_name, date_of_birth, address, email, program, year)
        result = execute_procedure(procedure_name, data)

        if "error" in result:
            return render_template("success_record.html", msg=result["error"])
        else:
            # Explicitly commit the transaction
            mysql.connection.commit()
            return render_template("success_record.html", msg="Student record added successfully")
    else:
        return "Method Not Allowed", 405
    
#show or read all students
@app.route("/student_info")
def student_info():
    query = "SELECT * FROM Students"
    
    cursor = None
    students = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        students = cursor.fetchall()

        current_year = datetime.now().year  # Calculate current year
        current_month = datetime.now().month  # Calculate current month
        current_day = datetime.now().day  # Calculate current day

        # Calculate age for each student
        for student in students:
            birth_year = student['birth_date'].year  # Assuming 'birth_date' is a datetime object in your student data
            birth_month = student['birth_date'].month  # Assuming 'birth_date' includes month
            age = current_year - birth_year

            if (current_month, current_day) < (birth_month, student['birth_date'].day):
                age -= 1

            student['age'] = age
            
    except mysql.connector.Error as err:
        msg = f"Failed to fetch student records: {err}"
        return render_template("success_record.html", msg="Student fetch successfully")
    finally:
        if cursor:
            cursor.close()

    return render_template("student_info.html", students=students, current_year=current_year, current_month=current_month, current_day=current_day)

# Function to verify user credentials
def verify_user(username, password):
    query = "SELECT * FROM Users WHERE username = %s AND password = %s"
    data = (username, password)
    result = execute_procedure(query, data)

    if result.get('result'):  # Check if 'result' key exists in the dictionary
        return True
    else:
        return False

#Bacalso's Work
# edit student
@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    if request.method == "POST":
        # Retrieve form data
        student_name = request.form["student_name"]
        date_of_birth = request.form["birth_date"]
        address = request.form["address"]
        email = request.form["institutional_email"]
        program = request.form["program"]
        year = request.form["year"]

        # Call the stored procedure to update a student
        procedure_name = "update_student"
        data = (student_id, student_name, date_of_birth, address, email, program, year)
        result = execute_procedure(procedure_name, data)

        if "error" in result:
            return render_template("success_record.html", msg=result["error"])
        else:
            return render_template("success_record.html", msg="Student record updated successfully")
    else:
        # Fetch student information using the 'student_id'
        query = "SELECT * FROM Students WHERE student_id = %s"
        data = (student_id,)
        
        try:
            cursor = mysql.connection.cursor()  # Ensure to use dictionary=True to fetch results as dictionaries
            cursor.execute(query, data)
            student = cursor.fetchone()  # Fetch the student details
            
            # Close the cursor after fetching the data
            cursor.close()
            
            return render_template("edit_student.html", student=student)
        except Exception as err:
            msg = f"Failed to fetch student record: {err}"
            return render_template("success_record.html", msg=msg)

# Delete Student using Stored Procedure
@app.route("/delete_student/<int:student_id>")
def delete_student(student_id):
    # Call the stored procedure to delete a student record
    procedure_name = "delete_student"
    data = (student_id,)
    result = execute_procedure(procedure_name, data)

    if "error" in result:
        return render_template("success_record.html", msg=result["error"])
    else:
        return render_template("success_record.html", msg="Student record deleted successfully")


# Create GWA
@app.route("/add_gwa", methods=["POST"])
def add_gwa():
    if request.method == "POST":
        student_name = request.form["student_name"]
        student_gwa = float(request.form["student_gwa"]) 

        procedure_name = "create_gwa"
        data = (student_name, student_gwa)
        result = execute_procedure(procedure_name, data)

        if result.get("error"):
            return render_template("success_record.html", msg=result["error"])
        else:
            return render_template("success_record.html", msg="GWA added successfully")
    else:
        return "Method Not Allowed", 405

# Fetch all GWAs
@app.route("/view_gwa")
def view_gwa():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM gwa")
        gwasa = cursor.fetchall()
        cursor.close()
        return render_template("view_gwa.html", gwasa=gwasa)
    except Exception as err:
        msg = f"Failed to fetch GWA records: {err}"
        return render_template("success_record.html", msg="Student fetched successfully")


#Tejano's work
# Update GWA
@app.route('/edit_gwa/<int:gwa_id>', methods=['GET', 'POST'])
def edit_gwa(gwa_id):
    if request.method == 'GET':
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM gwa WHERE id = %s", (gwa_id,))
            gwa_data = cursor.fetchone()
            cursor.close()
            
            return render_template('edit_gwa.html', gwa=gwa_data)
        except Exception as err:
            msg = f"Failed to fetch GWA record: {err}"
            return render_template("success_record.html", msg=msg)
    elif request.method == 'POST':
        try:
            cursor = mysql.connection.cursor()
            student_name = request.form['student_name']
            student_gwa = request.form['student_gwa']

            # Update the GWA data in the database
            update_query = "UPDATE gwa SET student_name = %s, student_gwa = %s WHERE id = %s"
            cursor.execute(update_query, (student_name, student_gwa, gwa_id))
            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('view_gwa'))  # Redirect to view_gwa route or any other desired endpoint
        except Exception as err:
            msg = f"Failed to update GWA record: {err}"
            return render_template("success_record.html", msg=msg)

# Delete GWA
@app.route("/delete_gwa/<int:gwa_id>")
def delete_gwa(gwa_id):
    procedure_name = "delete_gwa"
    data = (gwa_id,)
    result = execute_procedure(procedure_name, data)

    if "error" in result:
        return render_template("success_record.html", msg=result["error"])
    else:
        return render_template("success_record.html", msg="GWA deleted successfully")
    
#signup   
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Create a cursor to execute MySQL queries
        cur = mysql.connection.cursor()

        # Check if the username already exists
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            return jsonify({'message': 'Username already exists'}), 400

        # Insert new user into the 'users' table
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password))
        mysql.connection.commit()
        cur.close()

        return render_template('index.html', message="Signup successful")

    return jsonify({'message': 'Method Not Allowed'}), 405

#login condition
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
    user = cursor.fetchone()

    if user:
       
        session['username'] = user['username']
      
        return redirect('/index')
    else:
        
        return "Invalid username or password"  
    
#logout
@app.route("/logout")
def logout():
   
    if "username" in session:
        session.pop("username")
    
    
    return redirect("/")



    
if __name__ == '__main__':
    app.run(debug=True)