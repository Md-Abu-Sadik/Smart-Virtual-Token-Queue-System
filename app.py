from flask import Flask, render_template, request, redirect

import sqlite3

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

    conn = sqlite3.connect('appointments.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO appointments (name, phone, age, service) VALUES (?, ?, ?, ?)", 
                   (name, phone, age, service))
    conn.commit()
    conn.close()

    return redirect('/my_appointments') 

@app.route('/doctor_schedule')
def doctor_schedule():
    return render_template('doctor_schedule.html')

@app.route('/my_appointments')
def my_appointments():
    conn = sqlite3.connect('appointments.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments")
    data = cursor.fetchall()
    conn.close()
    return render_template('my_appointments.html', appointments=data)


@app.route('/manage_appointment')
def manage_appointment():
    return render_template('manage_appointment.html')


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
