import requests
import os
import zipfile
import json

class ItemsExtractor():
    def __init__(self):
        from app import logger
        self.logger = logger
        self.logger.info('Initialized ItemsExtractor')
        
    def download_jar(self, url, jar_path):
        os.makedirs(os.path.dirname(jar_path), exist_ok=True)
        if os.path.exists(jar_path):
            self.logger.info(f'Jar file has already been cached: {jar_path}')
            return
        try:
            self.logger.info(f'Starting download: {url} -> {jar_path}')
            with requests.get(url, stream=True, timeout=(300, 300)) as response:
                response.raise_for_status()
                with open(jar_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            self.logger.info(f'Jar file successfully downloaded: {jar_path}')
        except requests.exceptions.RequestException as e:
            if os.path.exists(jar_path):
                os.remove(jar_path)
            self.logger.error(f'Failed to download JAR from {url}: {e}')
            raise
        except OSError as e:
            if os.path.exists(jar_path):
                os.remove(jar_path)
            self.logger.error(f'File system error while saving JAR {jar_path}: {e}')
            raise
                
    def extract_items_from_jar(self, jar_path) -> list:
        items = set()
        tag_data = {}
        with zipfile.ZipFile(jar_path, 'r') as jar:
            for file_info in jar.filelist:
                if file_info.filename.startswith('data/minecraft/tags/item'):
                    with jar.open(file_info) as tag_file:
                        try:
                            tag_data: dict = json.load(tag_file)
                            for item_id in tag_data.get('values', []):
                                if isinstance(item_id, str):
                                    items.add(item_id)
                                elif isinstance(item_id, dict):
                                    items.add(item_id.get('id', ''))
                        except json.JSONDecodeError as e:
                            self.logger.error(f"JSON parse error in {file_info.filename}: {e}")
                            continue
                        
        return list(filter(lambda x: not x.startswith('#'), sorted(items)))
    
    def extract_entities_from_jar(self, jar_path) -> list:
        entities = set()
        entity_data = {}
        with zipfile.ZipFile(jar_path, 'r') as jar:
            entity_paths = [
                'data/minecraft/entity_types/', 
                'data/minecraft/tags/entity_type/'
            ]
            for path_prefix in entity_paths:
                for file_info in jar.filelist:
                    if file_info.filename.startswith(path_prefix):
                        with jar.open(file_info) as f:
                            try:
                                entity_data: dict = json.load(f)
                                for entity_id in entity_data.get('values', []):
                                    if isinstance(entity_id, str):
                                        entities.add(entity_id)
                                    elif isinstance(entity_id, dict):
                                        entities.add(entity_id.get('id', ''))
                            except json.JSONDecodeError as e:
                                self.logger.error(f"JSON parse error in {file_info.filename}: {e}")
                                continue
        return list(filter(lambda x: not x.startswith('#'), sorted(entities)))
    
    def get_items_and_entities(self, version_id, version_details) -> tuple[list, list]:
        jar_path = f'cache/jars/{version_id}.jar'
        client_url = version_details['downloads']['client']['url']
        
        self.logger.info(f'Downloading JAR file for version {version_id}')
        self.download_jar(client_url, jar_path)
        
        self.logger.info('Extracting items...')
        items = self.extract_items_from_jar(jar_path)
        
        self.logger.info('Extracting entities...')
        entities = self.extract_entities_from_jar(jar_path)
        
        
        return items, entities