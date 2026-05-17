from flask import Flask, Response, render_template, request, jsonify, flash
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
app.secret_key = '15062013Nd'
app.logger.info(f'Secret key: {app.secret_key}') # Delete in release

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
    try:
        data: dict = request.json
        entity = data.get('entity', 'zombie')
        position = data.get('position', '~ ~ ~')
        custom_name = data.get('customName', None)
        
        if custom_name:
            custom_name_snbt = {"CustomName": custom_name}
            command = f"summon minecraft:{entity} {position} {str(custom_name_snbt)}"
            flash('Команда успешно сгенерирована!', 'success')
            app.logger.info(f'Successfully generated SUMMON command: {command}')
            return jsonify({'command': command})
        else:
            command = f"summon minecraft:{entity} {position}"
            flash('Команда успешно сгенерирована!', 'success')
            app.logger.info(f'Successfully generated SUMMON command: {command}')
            return jsonify({'command': command})
    except Exception as e:
        flash('Ошибка при генерации команды.', 'error')
        app.logger.error(f'Error generating GIVE command: {str(e)}')
        jsonify({'error': str(e)}), 500

@app.route('/generate/give', methods=['POST'])
def generate_give() -> Response:
    try:
        data: dict = request.json
        target = data.get('player', '@p')
        item = data.get('item', 'cobblestone')
        count = data.get('count', 1)
        
        command = f"give {target} minecraft:{item} {count}"
        flash('Команда успешно сгенерирована!', 'success')
        app.logger.info(f'Generated GIVE command: {command}')
        return jsonify({'command': command})
    except Exception as e:
        flash('Ошибка при генерации команды.', 'error')
        app.logger.error(f'Error generating GIVE command: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    flash('Непредвиденная ошибка на сервере')
    app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning(f'404 Error: Page not found - {request.url}')
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run('0.0.0.0', 5000, debug=True)