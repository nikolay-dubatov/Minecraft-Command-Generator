from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)




if __name__ == "__main__":
    app.run('0.0.0.0')