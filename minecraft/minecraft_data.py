import requests
from datetime import datetime, timedelta
from . import minecraft_cache, items_extractor

class MinecraftData:
    def __init__(self, check_interval=2):
        from app import logger
        self.logger = logger
        self.logger.info('Initialized MinecraftData')
        
        self.base_url = "https://piston-meta.mojang.com/mc/game"
        self.check_interval = timedelta(hours=check_interval)
        self.last_manifest_check = None
        
        self.items_extractor = items_extractor.ItemsExtractor()
        self.cache = minecraft_cache.MinecraftCache()
    
    def get_versions_manifest(self) -> dict:
        """Gets all versions of Minecraft by `piston-meta`"""
        cache_key = 'versions_manifest'
        cached = self.cache.get(cache_key)
        debug = False
        
        if not debug:
            current_time = datetime.now()
            if (self.last_manifest_check is None or
                current_time - self.last_manifest_check >= self.check_interval):
                try:
            
                    url = f"{self.base_url}/version_manifest.json"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        self.logger.info('Successfuly fetched versions manifest')
                        data = response.json()
                        self.cache.set(cache_key, data)
                        self.last_manifest_check = current_time
                        return data
                    else:
                        raise Exception("Failed to fetch versions manifest")
                except Exception as e:
                    self.logger.error(f'Failed to update manifest: {str(e)}')
                
        if cached:
            return cached
        raise Exception('Failed to get versions manifest')
        
    def get_version_info(self, version_id) -> dict:
        manifest = self.get_versions_manifest()
        
        version_info = next(
            (v for v in manifest['versions'] if v['id'] == version_id),
            None
        )
        
        if not version_info:
            self.logger.error(f'Version {version_id} not found in the manifest')
            raise ValueError(f'Version {version_id} not found in the manifest')
        
        return version_info
    
    def get_version_details(self, version_id) -> dict:
        version_info = self.get_version_info(version_id)
        cached = self.cache.get(f'{version_id}_details')
        if not cached:
            response = requests.get(version_info['url'])
            if response.status_code == 200:
                data = response.json()
                self.cache.set(f'{version_id}_details', data)
                return data
            else:
                raise Exception(f'Failed to fetch version details: {response.status_code}')
        if cached: 
            return cached

    def get_versions_list(self) -> list:
        manifest = self.get_versions_manifest()
        versions = []
        for version in manifest['versions']:
            if version['type'] == 'release':
                versions.append(version)
        versions.sort(key=lambda x: x['releaseTime'], reverse=True)
        return versions

    def get_latest(self) -> str:
        manifest = self.get_versions_manifest()
        return manifest['latest']['release']

    def is_new_version_available(self, version_id) -> bool:
        manifest = self.get_versions_manifest()
        version_ids = [v['id'] for v in manifest[version_id]]
        return version_id in version_ids
    
    def _should_update_cache(self, version_id, data_type) -> bool:
        key = f'{data_type}_{version_id}'
        cached = self.cache.get(key)
        
        if not cached:
            return True
        
        version_info = self.get_version_info(version_id)
        return version_info is None
    
    def get_data_for_version(self, version_id, data_type):
        if self._should_update_cache(version_id, data_type):
            self.logger.info(f'Updating {data_type} cache for v{version_id}...')
            data = self._fetch_and_cache_data(version_id, data_type)
        else:
            cache_key = f'{data_type}_{version_id}'
            data = self.cache.get(cache_key)
        return data
    
    def _fetch_and_cache_data(self, version_id, data_type):
        version_details = self.get_version_details(version_id)
        items, entities = self.items_extractor.get_items_and_entities(version_id, version_details)
        data = items if data_type == 'items' else entities
        cache_key = f'{data_type}_{version_id}'
        self.cache.set(cache_key, data)
        return data
    
        