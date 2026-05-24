import json
from pathlib import Path
from datetime import datetime, timedelta

class MinecraftCache:
    def __init__(self, cache_dir='cache'):
        from app import logger
        self.logger = logger
        self.logger.info('Initialized MinecraftCache')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def _get_cache_path(self, key):
        return self.cache_dir / f"{key}.json"
    
    def _is_cache_valid(self, cache_path):
        if not cache_path.exists():
            return False
        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - file_time < self.check_interval
    
    def get(self, key, ttl_hours=None) -> None | dict:
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None
        
        if ttl_hours is None:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
            
        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - file_time < timedelta(hours=ttl_hours):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def set(self, key, data):
        cache_path = self._get_cache_path(key)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def delete(self, key):
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
            
    def clear(self):
        for cache_file in self.cache_dir.iterdir():
            if cache_file.is_file():
                cache_file.unlink()
                
    def cleanup_old_caches(self, days_to_keep=180):
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        for cache_file in self.cache_dir.iterdir():
            if cache_file.is_file():
                try:
                    file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        cache_file.unlink()
                        self.logger.info(f'Old cache deleted: {cache_file.name}')
                except Exception as e:
                    self.logger.error(f'Error deleting file {cache_file.name}')
                    
    def list_all_keys(self):
        return [f.stem for f in self.cache_dir.iterdir() if f.is_file()]