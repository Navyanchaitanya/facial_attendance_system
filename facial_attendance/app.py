from flask import Flask, render_template, request, redirect
import os
import csv
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        os.system(f"python recognizer.py register {name}")
        return redirect('/')
    return render_template('register.html')

@app.route('/attendance')
def attendance():
    os.system("python recognizer.py recognize")

    message = "⚠️ No message found"
    try:
        with open("last_message.txt", "r", encoding="utf-8") as f:
            message = f.read().strip()
    except Exception as e:
        message = f"Error reading message: {e}"

    return render_template("attendance.html", message=message)


import csv

@app.route('/log')
def view_log():
    log_data = []
    try:
        with open("attendance.csv", newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            log_data = list(reader)
    except FileNotFoundError:
        log_data = []

    return render_template("log.html", log_data=log_data)

if __name__ == "__main__":
    app.run(debug=True)
