from flask import Flask, Response, render_template, request, jsonify
from flask_cors import CORS
from logging.handlers import RotatingFileHandler
from minecraft.minecraft_data import MinecraftData
import logging
import os

if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = RotatingFileHandler(
    'logs/minecraft_generator.log', 
    maxBytes=10*1024*1024, 
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)


app = Flask(__name__)
CORS(app, resources={r"/api/*":{"origins":"*"}})
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
__all__ = ['logger']
try:
    mcdata = MinecraftData()
except Exception as e:
    logger.critical(f"Critical error during MinecraftData initialization: {e}")
    raise
app.secret_key = '15062013Nd'

@app.route('/')
@app.route('/home')
def home() -> str:
    return render_template('home.html', title="Home")

@app.route('/give_generator')
def give_generator() -> str:
    return render_template('generators/give_generator.html')

@app.route('/summon_generator')
def summon_generator() -> str:
    return render_template('generators/summon_generator.html')

@app.route('/api/minecraft/releases')
def get_versions_list() -> Response:
    try:
        releases = mcdata.get_versions_list()
        versions = []
        for release in releases:
            versions.append(release['id'])
        return jsonify({
            'success': True, 
            'versions': versions
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/minecraft/latest')
def get_latest() -> Response:
    latest = mcdata.get_latest()
    try:
        if latest:
            return jsonify({
                'success': True, 
                'latest': latest
            })
        return jsonify({
            'success': False, 
            'error': 'Latest release not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/minecraft/<data_type>/<version_id>')
def get_data(data_type, version_id) -> Response:
    if data_type not in ['items', 'entities']:
        return jsonify({
            'success': False, 
            'error': 'Incorrect type (not items or entities)'
        }), 400
    try:
        data = mcdata.get_data_for_version(version_id, data_type)
        return jsonify({
            'success': True, 
            'data': data
        })
    except ValueError as e:
        logger.error(e)
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(e)
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/generate/summon', methods=['post'])
def generate_summon() -> Response:
    try:
        data: dict = request.json
        entity = data.get('entity', 'zombie')
        x = data.get('x-field')
        y = data.get('x-field')
        z = data.get('z-field')
        position = ' '.join([x, y, z])
        custom_name = data.get('custom-name', None)
        
        if custom_name:
            custom_name_snbt = {"CustomName": custom_name}
            command = f"summon minecraft:{entity} {position} {str(custom_name_snbt)}"
        else:
            command = f"summon {entity} {position}"
        logger.info(f'Successfully generated SUMMON command: {command}')
        return jsonify({
                'command': command, 
                'success': True, 
                'message': 'Команда сгенерирована'
            })
    except Exception as e:
        logger.error(f'Error generating GIVE command: {str(e)}')
        return jsonify({
            'error': 'Ошибка генерации команды', 
            'success': False
        }), 500

@app.route('/generate/give', methods=['POST'])
def generate_give() -> Response:
    try:
        data: dict = request.json
        target = data.get('player', '@p')
        item = data.get('item', 'cobblestone')
        count = data.get('count', 1)
        
        command = f"give {target} {item} {count}"
        logger.info(f'Generated GIVE command: {command}')
        return jsonify({
            'command': command, 
            'success': True, 
            'message': 'Команда сгенерирована'
        })
    except Exception as e:
        logger.error(f'Error generating GIVE command: {str(e)}')
        return jsonify({
            'error': 'Ошибка генерации команды', 
            'success': False
        }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f'404 Error: Page not found - {request.url}')
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run('0.0.0.0', 5000, debug=False)