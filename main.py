from flask import Flask, request, jsonify
from users import get_all_users, get_user_by_id, create_user, update_user, delete_user
from flask_mysqldb import MySQL
from database import set_database
from dotenv import load_dotenv
from os import getenv

app = Flask(__name__)

load_dotenv()

app.config["MYSQL_HOST"] = getenv("MYSQL_HOST")
#app.config["MYSQL_PORT"] = int(getenv("MYSQL_PORT"))
app.config["MYSQL_USER"] = getenv("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = getenv("MYSQL_DB")
# to return results as dictionaries and not an array
app.config["MYSQL_CURSORCLASS"] = getenv("MYSQL_CURSORCLASS")
app.config["MYSQL_AUTOCOMMIT"] = True if getenv("MYSQL_AUTOCOMMIT") == "True" else False

mysql = MySQL(app)
set_database(mysql)

@app.route("/")
def home():
  return "<h1>Hello, World!</h1>"


@app.route("/users", methods=["GET", "POST"])
def users():
  if request.method == "POST":
    data = request.get_json()
    result = create_user(data)
  else:
    result = get_all_users()
  return jsonify(result)


@app.route("/users/<id>", methods=["GET", "PUT", "DELETE"])
def users_by_id(id):
  if request.method == "PUT":
    data = request.get_json()
    result = update_user(id, data)
  elif request.method == "DELETE":
    result = get_user_by_id(id)
    if result is not None:
      result = delete_user(id)
    else:
      result = {"error": "User not found"}
  else:
    result = get_user_by_id(id)
  return jsonify(result)
