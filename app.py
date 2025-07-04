from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/token')
def token():
    return render_template('token.html')

if __name__ == '__main__':
    app.run(debug=True)
