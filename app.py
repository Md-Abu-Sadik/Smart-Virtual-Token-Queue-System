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

@app.route('/doctor_schedule')
def doctor_schedule():
    return render_template('doctor_schedule.html')

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
    name = request.form.get('name')
    service = request.form.get('service')
    phone = request.form.get('phone')  # ✅ Required
    appointment_id = request.form.get('appointment_id')  # ❌ Optional

    # Simple validation for required fields
    if not name or not service or not phone:
        return "Name, service, and phone number are required!", 400

    tokens = load_tokens()
    token_number = f"{service[0].upper()}-{len(tokens) + 1:03d}"

    token = {
        "number": token_number,
        "name": name,
        "phone": phone,
        "service": service,
        "appointment_id": appointment_id if appointment_id else None,
        "status": "Pending"
    }

    tokens.append(token)
    save_tokens(tokens)

    return render_template("token_success.html", token=token)


@app.route('/token', methods=['POST'])
def generate_token():
    name = request.form.get('name')
    phone = request.form.get('phone')
    service = request.form.get('service')
    appointment_id = request.form.get('appointment_id')  # Optional

    if not name or not phone or not service:
        return "Missing required fields", 400

    tokens = load_tokens()

    token_number = f"{service[0].upper()}-{len(tokens)+1:03d}"

    token = {
        "number": token_number,
        "name": name,
        "phone": phone,
        "service": service,
        "appointment_id": appointment_id,
        "status": "Pending"
    }

    tokens.append(token)
    save_tokens(tokens)

    return render_template("token_success.html", token=token)


@app.route('/token_status')
def token_status():
    tokens = load_tokens()  
    services = sorted({token['service'] for token in tokens}) if tokens else []
    return render_template('token_status.html', tokens=tokens, services=services)

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

@app.route('/manage_appointment', methods=['GET', 'POST'])
def manage_appointment():
    if request.method == 'POST':
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

    # For GET request — load the form/page to cancel/reschedule
    appointments = load_appointments()
    return render_template("manage_appointment.html", appointments=appointments)


if __name__ == '__main__':
    app.run(debug=True)