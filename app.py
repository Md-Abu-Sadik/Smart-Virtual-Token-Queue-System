from flask import Flask, render_template, request, redirect
import uuid
import os
import json

app = Flask(__name__)

# ---------- File Paths ----------
APPOINTMENTS_FILE = 'appointments.json'
TOKENS_FILE = 'tokens.json'

# ---------- Utility Functions ----------
def load_appointments():
    if os.path.exists(APPOINTMENTS_FILE):
        with open(APPOINTMENTS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_appointments(data):
    with open(APPOINTMENTS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_tokens(data):
    with open(TOKENS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/book_appointment')
def book_appointment():
    return render_template('book_appointment.html')

@app.route('/submit_appointment', methods=['POST'])
def submit_appointment():
    appointments = load_appointments()
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
        'status': 'Booked'
    }

    appointments.append(new_appt)
    save_appointments(appointments)

    return render_template("appointment_success.html", appointment_id=appointment_id)

@app.route('/get_token', methods=['POST'])
def get_token():
    tokens = load_tokens()
    name = request.form['name']
    service = request.form['service']
    appointment_id = request.form.get('appointment_id')

    # Create token number
    service_initial = service[0].upper()
    count = sum(1 for t in tokens if t['service'] == service)
    token_number = f"{service_initial}-{count + 1:03d}"

    token = {
        "number": token_number,
        "name": name,
        "service": service,
        "appointment_id": appointment_id,
        "status": "Pending"
    }

    tokens.append(token)
    save_tokens(tokens)

    return render_template("token_success.html", token=token)

@app.route('/admin')
def admin_panel():
    tokens = load_tokens()
    return render_template("admin.html", tokens=tokens)

@app.route('/update_token', methods=['POST'])
def update_token():
    token_number = request.form.get('token_number')
    name = request.form.get('name')
    tokens = load_tokens()

    updated = False
    for token in tokens:
        if token.get('number') == token_number and token.get('name') == name:
            token['status'] = 'Completed'
            updated = True

    if updated:
        save_tokens(tokens)

    return redirect('/admin')

@app.route('/my_appointments')
def my_appointments():
    appointments = load_appointments()
    return render_template("my_appointments.html", appointments=appointments)

@app.route('/manage_appointment', methods=['POST'])
def manage_appointment():
    appointments = load_appointments()
    appointment_id = request.form['appointment_id']
    action = request.form['action']

    index = next((i for i, a in enumerate(appointments) if a.get('id') == appointment_id), None)

    if index is not None:
        if action == 'cancel':
            appointments.pop(index)
        elif action == 'reschedule':
            appointments[index]['status'] = 'Rescheduled'
        save_appointments(appointments)

    return redirect('/my_appointments')

if __name__ == '__main__':
    app.run(debug=True)