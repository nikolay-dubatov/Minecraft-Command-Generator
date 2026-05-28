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
        self.cache.cleanup_old_caches()
        self.cache_latest()
    
    def cache_latest(self) -> None:
        latest = self.get_latest()
        for key in ("items", "entities"):
            cached = self.cache.get(key, latest, 24)
            if cached: continue
        if cached: return
        self._fetch_and_cache_data(latest, ("items", "entities"))
    
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
            raise ValueError(f'Version {version_id} not found in the manifest')
        
        return version_info
    
    def get_version_details(self, version_id) -> dict:
        version_info = self.get_version_info(version_id)
        cached = self.cache.get('details', version_id)
        if not cached:
            response = requests.get(version_info['url'])
            if response.status_code == 200:
                data = response.json()
                self.cache.set('details', data, version_id)
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
        key = data_type
        cached = self.cache.get(key, version_id)
        
        if not cached:
            return True
        try:
            version_info = self.get_version_info(version_id)
        except ValueError as e:
            self.logger.error(e)
            return
        return version_info is None
    
    def get_data_for_version(self, version_id, data_type):
        if self._should_update_cache(version_id, data_type):
            self.logger.info(f'Updating {data_type} cache for v{version_id}...')
            data = self._fetch_and_cache_data(version_id, data_type)
        else:
            cache_key = data_type
            data = self.cache.get(cache_key, version_id)
        return data
    
    def _fetch_and_cache_data(self, version_id, data_type):
        try:
            version_details = self.get_version_details(version_id)
        except ValueError as e:
            self.logger.error(e)
            return
        items, entities = self.items_extractor.get_items_and_entities(version_id, version_details)
        if isinstance(data_type, str):
            data = items if data_type == 'items' else entities
            cache_key = data_type
            self.cache.set(cache_key, data, version_id)
        elif isinstance(data_type, tuple):
            for key in data_type:
                self.cache.set(key, globals()[key])
        return data
    
        