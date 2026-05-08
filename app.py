from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
@app.route('/home')
def home() -> str:
    return render_template('home.html', title="Home")

if __name__ == "__main__":
    app.run('0.0.0.0', 5000, debug=False)