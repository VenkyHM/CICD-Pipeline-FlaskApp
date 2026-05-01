from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import certifi
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ✅ Safe config with fallback
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/testdb")
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# ✅ Initialize Mongo safely
try:
    mongo = PyMongo(app, tlsCAFile=certifi.where())
except Exception as e:
    print("MongoDB connection error:", e)

# ---------------- ROUTES ---------------- #

# Home page -> list students
@app.route('/')
def index():
    try:
        students = mongo.db.students.find()
        return render_template('index.html', students=students)
    except Exception as e:
        return f"Error fetching data: {str(e)}"

# Add student
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            course = request.form.get('course')

            mongo.db.students.insert_one({
                "name": name,
                "email": email,
                "course": course
            })
            return redirect(url_for('index'))
        except Exception as e:
            return f"Error adding student: {str(e)}"

    return render_template('add_student.html')

# Update student
@app.route('/update/<student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    try:
        student = mongo.db.students.find_one({"_id": ObjectId(student_id)})
    except Exception as e:
        return f"Error loading student: {str(e)}"

    if request.method == 'POST':
        try:
            new_name = request.form.get('name')
            new_email = request.form.get('email')
            new_course = request.form.get('course')

            mongo.db.students.update_one(
                {"_id": ObjectId(student_id)},
                {"$set": {
                    "name": new_name,
                    "email": new_email,
                    "course": new_course
                }}
            )
            return redirect(url_for('index'))
        except Exception as e:
            return f"Error updating student: {str(e)}"

    return render_template('update_student.html', student=student)

# Delete student
@app.route('/delete/<student_id>')
def delete_student(student_id):
    try:
        mongo.db.students.delete_one({"_id": ObjectId(student_id)})
        return redirect(url_for('index'))
    except Exception as e:
        return f"Error deleting student: {str(e)}"

# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)

