from dataclasses import dataclass, asdict
from os import path, environ

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@dataclass
class Config:
    """기본 Configuration"""
    
    BASE_DIR = base_dir
    
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
    

@dataclass
class LocalConfig(Config):
    PROJ_RELOAD: bool = True


@dataclass
class ProdConfig(Config):
    # 운영서버(Production Server)
    PROJ_RELOAD: bool = False
    

def conf():
    """환경에 따라 fastapi reload 설정 및 환경 불러오기"""
    config = dict(prod=ProdConfig(), local=LocalConfig())
    return config.get(environ.get("API_ENV", "local"))
