from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os
import json



app = Flask(__name__)
app.secret_key = 'super_secret_key' 

# ---------- File Paths ----------
APPOINTMENTS_FILE = 'appointments.json'
TOKENS_FILE = 'tokens.json'
ADMIN_USERS_FILE = 'admin_users.json'

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


def load_admins():
    if not os.path.exists(ADMIN_USERS_FILE):
        return []
    with open(ADMIN_USERS_FILE, 'r') as f:
        return json.load(f)

def save_admins(users):
    with open(ADMIN_USERS_FILE, 'w') as f:
        json.dump(users, f) 


# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/book_appointment')
def book_appointment():
    doctor_name = request.args.get('doctor', 'Not Assigned')
    time = request.args.get('time', '') 
    return render_template('book_appointment.html', doctor_name=doctor_name , time=time)

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
    doctor = request.form.get('doctor', '')  # ✅ New line
    appointment_id = str(uuid.uuid4())[:8]
    date = request.form['date']
    time = request.form.get('time', '')

    new_appt = {
        'id': appointment_id,
        'name': name,
        'phone': phone,
        'age': age,
        'service': service,
        'status': 'Booked',
        'date': date,
        'doctor': doctor,    # ✅ Just using the variable
        'time': time
    }

    appointments.append(new_appt)
    save_appointments(appointments)

    return render_template("appointment_success.html", appointment_id=appointment_id)



@app.route('/get_token', methods=['POST'])
def get_token():
    name = request.form.get('name')
    service = request.form.get('service')
    phone = request.form.get('phone')
    date = request.form.get('date')  
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
    date = request.form['date']


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
    "status": "Pending",
    "date": date  # ✅ No comma here
    }

    tokens.append(token)
    save_tokens(tokens)

    return render_template("token_success.html", token=token)


@app.route('/token_status')
def token_status():
    tokens = load_tokens()
    for token in tokens:
        if 'date' in token and token['date']:
            try:
                token['date'] = datetime.strptime(token['date'], "%Y-%m-%d").strftime("%d-%m-%Y")
            except ValueError:
                pass   
    services = sorted({token['service'] for token in tokens}) if tokens else []
    return render_template('token_status.html', tokens=tokens, services=services)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user_input = request.form['username']  # Username or Email
        password = request.form['password']
        admins = load_admins()
        for user in admins:
            # Check both username and email fields
            if (user['username'] == user_input or user.get('email') == user_input) and check_password_hash(user['password'], password):
                session['admin_user'] = user['username']
                session['admin_name'] = user.get('name', user['username'])
                return redirect(url_for('admin_panel'))
        flash('Invalid username or password.')
    return render_template('admin_login.html')



@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        admins = load_admins()

        # Username or Email already exists check
        if any(u['username'] == username for u in admins):
            flash('Username already exists.')
        elif any(u.get('email') == email for u in admins):
            flash('Email already exists.')
        elif password != confirm_password:
            flash('Passwords do not match.')
        else:
            admins.append({
                'name': name,
                'username': username,
                'email': email,
                'password': generate_password_hash(password)
            })
            save_admins(admins)
            flash('Registration successful. Please log in.')
            return redirect(url_for('admin_login'))

    return render_template('admin_register.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_user', None)
    return redirect(url_for('admin_login'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('admin_email', None)
    return redirect(url_for('admin_login'))  # or your login page

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    # ✅ Require admin login
    if 'admin_user' not in session:
        return redirect(url_for('admin_login'))

    tokens = load_tokens()
    today = datetime.now().strftime('%Y-%m-%d')
    today_count = sum(1 for token in tokens if token.get("date") == today)

    if request.method == 'POST':
        token_number = request.form.get('token_number')
        new_status = request.form.get('new_status')
        # Only update if both provided
        if token_number and new_status:
            for token in tokens:
                if token.get('number') == token_number:
                    token['status'] = new_status
                    break
            save_tokens(tokens)
            flash("Token status updated!", "success")
            # Optionally: redirect to avoid form resubmission on refresh
            return redirect(url_for('admin_panel'))

    # 👇 Add this to pass admin_name to the template
    return render_template("admin.html", tokens=tokens, today_count=today_count, admin_name=session.get('admin_name', 'Admin'))


@app.route('/update_token', methods=['POST'])
def update_token():
    token_number = request.form.get('token_number')
    name = request.form.get('name')
    new_status = request.form.get('new_status')
    tokens = load_tokens()
    with open(TOKENS_FILE, 'r') as f:
        tokens = json.load(f)

    updated = False
    for token in tokens:
        if token.get('number') == token_number and token.get('name') == name:
            token['status'] = new_status  # ✅ Use selected status
            updated = True

    if updated:
        save_tokens(tokens)

    return redirect('/admin')

@app.route('/my_appointments')
def my_appointments():
    appointments = load_appointments()
    for appt in appointments:
        if 'date' in appt and appt['date']:
            try:
                appt['date'] = datetime.strptime(appt['date'], "%Y-%m-%d").strftime("%d-%m-%Y")
            except ValueError:
                pass 
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
                new_datetime = request.form.get('new_time')  # e.g. "2025-07-18T14:00"
                if new_datetime:
                    try:
                        dt_obj = datetime.strptime(new_datetime, "%Y-%m-%dT%H:%M")
                        appointments[index]['date'] = dt_obj.strftime("%Y-%m-%d")
                        appointments[index]['time'] = dt_obj.strftime("%I:%M %p")
                    except ValueError:
                        pass
                appointments[index]['status'] = 'Rescheduled'
            
            save_appointments(appointments)

        return redirect('/my_appointments')

    # For GET request — load the form/page to cancel/reschedule
    appointments = load_appointments()
    return render_template("manage_appointment.html", appointments=appointments)

@app.route('/select_doctor', methods=['POST'])
def select_doctor():
    doctor_name = request.form.get('doctor_name')
    doctor_time = request.form.get('time')
    return redirect(url_for('book_appointment', doctor=doctor_name ,time=doctor_time ))



@app.route('/display')
def display_token():
    tokens = load_tokens()
    now_serving = next((t for t in tokens if t['status'] == 'Processing'), None)
    current_time = datetime.now().strftime("%I:%M %p")
    return render_template("display.html", token=now_serving, current_time=current_time)


@app.route("/history", methods=["GET"])
def view_history():
    date_filter = request.args.get("date")
    service_filter = request.args.get("service")

    tokens = load_tokens()

    filtered_tokens = tokens
    if date_filter:
        filtered_tokens = [t for t in filtered_tokens if t.get("date") == date_filter]

    if service_filter and service_filter != "":
        filtered_tokens = [t for t in filtered_tokens if t.get("service") == service_filter]

    return render_template("history.html", tokens=filtered_tokens)

@app.route("/reset_today", methods=["POST"])
def reset_today():
    tokens = load_tokens()
    today = datetime.now().strftime('%Y-%m-%d')
    updated_tokens = [t for t in tokens if t.get("date") != today]
    save_tokens(updated_tokens)
    return redirect(url_for("admin_panel"))

@app.route("/reset_all", methods=["POST"])
def reset_all():
    # Just clear all tokens
    save_tokens([])
    return redirect(url_for("admin_panel"))

if __name__ == '__main__':
    app.run(debug=True)