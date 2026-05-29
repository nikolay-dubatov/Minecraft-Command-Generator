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
                filename = file_info.filename
                if ((filename.startswith('data/minecraft/recipe') or
                     filename.startswith('data/minecraft/loot_table') or
                     filename.startswith('data/minecraft/tags/item')) and 
                    filename.endswith('.json')):
                    with jar.open(file_info) as file:
                        try:
                            data: dict = json.load(file)
                            self._extract_from_recipes(data, items)
                            self._extract_from_loot_tables(data, items)
                            self._extract_from_tags(data, items)
                        except json.JSONDecodeError as e:
                            self.logger.error(f"JSON parse error in {file_info.filename}: {e}")
                            continue
        
        items.update({
            'minecraft:barrier',
            'minecraft:light',
            'minecraft:structure_block',
            'minecraft:jigsaw',
            'minecraft:command_block',
            'minecraft:repeating_command_block',
            'minecraft:chain_command_block', 
            'minecraft:test_block', 
            'minecraft:test_instance_block',
        })
        return list(filter(lambda x: not x.startswith('#'), sorted(items)))
    
    def _extract_from_loot_tables(self, data: dict, items: set) -> None:
        if isinstance(data, dict):
            if 'type' in data and data['type'] == 'item' and 'name' in data:
                items.add(data['name'])
            if 'pools' in data:
                for pool in data['pools']:
                    if 'entries' in pool:
                        for entry in pool['entries']:
                            self._extract_from_table_entry(entry, items)
            for key, value in data.items():
                self._extract_from_loot_tables(value, items)
        elif isinstance(data, list):
            for item in data:
                self._extract_from_loot_tables(item, items)
                
    def _extract_from_table_entry(self, entry: dict, items: set) -> None:
        if 'type' in entry and entry['type'] == 'minecraft:item':
            if 'name' in entry:
                items.add(entry['name'])
        elif 'children' in entry:
            for child in entry['children']:
                self._extract_from_table_entry(child, items)
        
    def _extract_from_tags(self, data: dict, items: set) -> None:
        if 'values' in data:
            for value in data['values']:
                if isinstance(value, str):
                    items.add(value)
                elif isinstance(value, dict) and 'id' in value:
                    items.add(value['id'])
        
    def _extract_from_recipes(self, data: dict, items: set) -> None:
        if isinstance(data, dict):
            # 1. recipe result
            if 'result' in data:
                result = data['result']
                if isinstance(result, dict) and 'id' in result:
                    items.add(result['id'])
                elif isinstance(result, str):
                    items.add(result)
            
            # 2. recipe ingredients
            if 'ingredients' in data:
                for ingredient in data['ingredients']:
                    if isinstance(ingredient, str):
                        if not ingredient.startswith('#'):
                            items.add(ingredient)
                    elif isinstance(ingredient, dict):
                        self._extract_ingredient_ids(ingredient, items)
            
            # 3. Recursive traversal of other fields
            for key, value in data.items():
                if key not in ['result', 'ingredients']:
                    self._extract_from_recipes(value, items)
        elif isinstance(data, list):
            for item in data:
                self._extract_from_recipes(item, items)
                
    def _extract_ingredient_ids(self, ingredient: dict, items: set) -> None:
        if 'item' in ingredient:
            items.add(ingredient['items'])
        elif 'tag' in ingredient:
            pass
        for key, value in ingredient.items():
            if key not in ['item', 'tag']:
                if isinstance(value, dict):
                    self._extract_ingredient_ids(value, items)
                elif isinstance(value, list):
                    for v in value:
                        if isinstance(v, dict):
                            self._extract_ingredient_ids(v, items)
        
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