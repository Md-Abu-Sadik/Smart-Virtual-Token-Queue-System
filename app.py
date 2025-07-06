from flask import Flask, render_template, request, redirect
from flask import render_template
import sqlite3
import uuid
import os
import json
from flask import Flask

app = Flask(__name__)

DATA_FILE = 'appointments.json' 

def load_appointments():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_appointments(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

appointments = load_appointments()  

# Token counter (for demo use only – resets on app restart)
token_counter = {
    "Dental": 1,
    "Eye Checkup": 1,
    "General Physician": 1
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/token', methods=['POST'])
def token():
    name = request.form['name']
    service = request.form['service']
    
    token_prefix = {
        "Dental": "D",
        "Eye Checkup": "E",
        "General Physician": "G"
    }.get(service, "X")

    number = token_counter[service]
    token_number = f"{token_prefix}-{number:03d}"
    token_counter[service] += 1

    return render_template('token.html', name=name, service=service, token=token_number)


@app.route('/book_appointment')
def book_appointment():
    return render_template('book_appointment.html')

@app.route('/submit_appointment', methods=['POST'])
def submit_appointment():
    name = request.form['name']
    phone = request.form['phone']
    age = request.form['age']
    service = request.form['service']
    appointment_id = str(uuid.uuid4())[:8]

    new_appt = {
        'id': appointment_id,
        'name': name,
        'phone': phone,
        'age': age,
        'service': service,
        'doctor': 'Dr. Ahsan',
        'date': '2025-07-08',
        'time': '10:30 AM'
    }

    appointments.append(new_appt)
    save_appointments(appointments)

    return render_template("appointment_success.html", appointment_id=appointment_id)

@app.route('/doctor_schedule')
def doctor_schedule():
    return render_template('doctor_schedule.html')

@app.route('/my_appointments')
def my_appointments():
    conn = sqlite3.connect('appointments.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments")
    appointments = cursor.fetchall()
    conn.close()
    return render_template("my_appointments.html", appointments=appointments)


@app.route('/manage_appointment', methods=['GET', 'POST'])
def manage_appointment():
    message = ''
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        action = request.form['action']
        index = next((i for i, a in enumerate(appointments) if a['id'] == appointment_id), None)

        if index is not None:
            if action == 'cancel':
                appointments.pop(index)
                save_appointments(appointments)
                message = f"Appointment {appointment_id} canceled."
            elif action == 'reschedule':
                appointments[index]['time'] = "1:00 PM"  # Simulate rescheduling
                save_appointments(appointments)
                message = f"Appointment {appointment_id} rescheduled."
        else:
            message = "Appointment ID not found."

    return render_template('manage_appointment.html', message=message)



@app.route('/token_status')
def token_status():
    return render_template('token_status.html')

def init_db():
    conn = sqlite3.connect('appointments.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            age INTEGER NOT NULL,
            service TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call it once when app starts
init_db()





if __name__ == '__main__':
    app.run(debug=True)
