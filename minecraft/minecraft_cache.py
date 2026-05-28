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
        
    def _get_cache_path(self, key: str, version: str | None = None) -> Path:
        version_dir: Path = self.cache_dir / version if version else self.cache_dir
        version_dir.mkdir(parents=True, exist_ok=True)
        return version_dir / f'{key}.json'
    
    def get(self, key, version=None, ttl_hours=None) -> None | dict:
        cache_path = self._get_cache_path(key, version)
        if not cache_path.exists():
            return None
        
        if ttl_hours is not None:
            file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
            if datetime.now() - file_time > timedelta(hours=ttl_hours):
                self.logger.debug(f'Cache expired: {cache_path}')
                return None
        
        try:
            data = json.loads(cache_path.read_text(encoding='utf-8'))
            self.logger.debug(f'Cache hit: {cache_path}')
            return data
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self.logger.error(f'Error reading cache file {cache_path}: {e}')
            return None
    
    def set(self, key: str, data: dict, version: str=None) -> None:
        cache_path = self._get_cache_path(key, version)
        try:
            cache_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), 
                encoding='utf-8'
            )
            self.logger.info(f'Cache saved: {cache_path}')
        except (OSError, TypeError) as e:
            self.logger.error(f'Error saving cache file {cache_path}: {e}')
            
    def delete(self, key: str, version: str=None) -> None:
        cache_path = self._get_cache_path(key, version)
        if cache_path.exists():
            try:
                cache_path.unlink()
                self.logger.info(f'Cache deleted: {cache_path}')
                return True
            except OSError as e:
                self.logger.error(f'Error deleting cache file {cache_path}: {e}')
                return False
        return False
            
    def clear(self) -> None:
        try:
            for item in self.cache_dir.iterdir():
                if item.is_dir():
                    self._remove_directory(item)
                elif item.is_file():
                    item.unlink()
            self.logger.info('Cache cleared completely')
        except OSError as e:
            self.logger.error(f'Error clearing cache: {e}')
            
    def _remove_dir(self, dir: Path):
        for item in dir.iterdir():
            if item.is_dir():
                self._remove_dir(item)
            else:
                item.unlink()
        dir.rmdir()
                
    def cleanup_old_caches(self, days_to_keep=180) -> None:
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
                    
    def list_all_keys(self) -> list[str]:
        keys = []
        for file_path in self.cache_dir.rglob('*.json'):  # только JSON‑файлы
            if file_path.is_file():
                # Извлекаем ключ и версию для структурированного вывода
                relative = file_path.relative_to(self.cache_dir)
                if len(relative.parts) > 1:  # есть версия
                    keys.append(f"{relative.parts[0]}/{relative.stem}")
                else:  # нет версии
                    keys.append(relative.stem)
        return keys