from flask import Flask, Response, render_template, request, jsonify
from flask_cors import CORS
from logging.handlers import RotatingFileHandler
import json
import logging
import os

if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = RotatingFileHandler(
    'logs/minecraft_generator.log', 
    maxBytes=10240, 
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s'
))
file_handler.setLevel(logging.INFO)

app = Flask(__name__)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Minecraft Command Generator startup')
CORS(app)
def load_minecraft_data() -> dict:
    with open('data/data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

data = load_minecraft_data()

@app.route('/')
@app.route('/home')
def home() -> str:
    return render_template('home.html', title="Home")

@app.route('/give_generator')
def give_generator() -> str:
    return render_template('generators/give_generator.html', items = data['items'])

@app.route('/summon_generator')
def summon_generator() -> str:
    return render_template('generators/summon_generator.html', entities=data['entities'])

@app.route('/generate/summon', methods=['post'])
def generate_summon() -> Response:
    data: dict = request.json
    entity = data.get('entity', 'zombie')
    position = data.get('position', '~ ~ ~')
    custom_name = data.get('customName', None)
    app.logger.info(f'Generate SUMMON command: {entity=}, {position=}, {custom_name=}')
    
    if custom_name:
        custom_name_snbt = {"CustomName": custom_name}
        command = f"summon minecraft:{entity} {position} {str(custom_name_snbt)}"
        app.logger.info(f'Generated SUMMON command: {command}')
        return jsonify({'command': command})
    else:
        command = f"summon minecraft:{entity} {position}"
        app.logger.info(f'Generate SUMMON command: {command}')
        return jsonify({'command': command})

@app.route('/generate/give', methods=['POST'])
def generate_give() -> Response:
    data: dict = request.json
    target = data.get('player', '@p')
    item = data.get('item', 'cobblestone')
    count = data.get('count', 1)
    app.logger.info(f'Generate GIVE command: {target=}, {item=}, {count=}')
    
    command = f"give {target} minecraft:{item} {count}"
    app.logger.info(f'Generated GIVE command: give {target} minecraft:{item} {count}')
    return jsonify({'command': command})

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    app.run('0.0.0.0', 5000, debug=True)