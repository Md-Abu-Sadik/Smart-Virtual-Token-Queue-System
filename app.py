from flask import Flask, render_template, request

app = Flask(__name__)

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
    return f"<h2>Appointment booked for {name} ({service})</h2>"

@app.route('/doctor_schedule')
def doctor_schedule():
    return render_template('doctor_schedule.html')

@app.route('/my_appointments')
def my_appointments():
    return render_template('my_appointments.html')

@app.route('/manage_appointment')
def manage_appointment():
    return render_template('manage_appointment.html')


if __name__ == '__main__':
    app.run(debug=True)
