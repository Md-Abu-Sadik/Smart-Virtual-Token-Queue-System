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
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []  
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

def load_appointments():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []  

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/get_token', methods=['POST'])
def get_token():
    name = request.form['name']
    service = request.form['service']
    appointment_id = request.form.get('appointment_id')  # Optional field

    token_number = token_counter.get(service, 1)
    token_counter[service] = token_number + 1

    # Create token
    token = {
        "id": str(uuid.uuid4()),
        "name": name,
        "service": service,
        "token_number": token_number,
        "appointment_id": appointment_id,
        "status": "Pending"  # ✅ Standardized to match admin panel logic
    }

    # ✅ Save token to tokens.json
    tokens = []
    if os.path.exists('tokens.json'):
        with open('tokens.json', 'r') as f:
            try:
                tokens = json.load(f)
            except json.JSONDecodeError:
                tokens = []

    tokens.append(token)

    with open('tokens.json', 'w') as f:
        json.dump(tokens, f, indent=4)

    # ✅ Return success page
    return render_template("token_success.html", token=token)



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
    appointments = load_appointments()
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
    tokens = load_appointments()
    services = sorted({token['service'] for token in tokens})
    return render_template('token_status.html', tokens=tokens, services=services)

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


@app.route('/token', methods=['POST'])
def generate_token():
    name = request.form.get('name')
    service = request.form.get('service')
    appointment_id = request.form.get('appointment_id')  # Optional

    # Load existing tokens
    tokens = load_appointments()

    # Count how many tokens exist for this service
    existing_tokens = [t for t in tokens if t["service"] == service]
    token_number = f"{service[0].upper()}-{len(existing_tokens) + 1:03d}"

    # Create new token
    token = {
        "number": token_number,
        "name": name,
        "service": service,
        "appointment_id": appointment_id
    }

    # Save new token
    tokens.append(token)
    save_appointments(tokens)

    return render_template('token_success.html', token=token)


@app.route('/admin')
def admin_panel():
    with open('appointments.json') as f:
        tokens = json.load(f)
    return render_template('admin.html', tokens=tokens)

# Update token status
@app.route('/update_token/<token_number>')
def update_token(token_number):
    name = request.args.get('name')  # Get the name from query string

    # Load appointments from JSON
    with open('appointments.json', 'r') as f:
        appointments = json.load(f)

    # Update the matching token (both number and name must match)
    for token in appointments:
        if token.get('number') == token_number and token.get('name') == name:
            token['status'] = 'Completed'
            break

    # Save changes back to JSON
    with open('appointments.json', 'w') as f:
        json.dump(appointments, f, indent=4)

    return redirect('/admin')# or wherever you want to go





if __name__ == '__main__':
    app.run(debug=True)
