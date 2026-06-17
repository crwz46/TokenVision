import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
    BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "")
    POLYGONSCAN_API_KEY = os.getenv("POLYGONSCAN_API_KEY", "")
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
    CACHE_DIR = os.getenv("CACHE_DIR", ".cache")
    PORT = int(os.getenv("PORT", "8000"))
    HOST = os.getenv("HOST", "0.0.0.0")

    @classmethod
    def has_etherscan_key(cls) -> bool:
        return bool(cls.ETHERSCAN_API_KEY)

    @classmethod
    def has_bscscan_key(cls) -> bool:
        return bool(cls.BSCSCAN_API_KEY)

    @classmethod
    def has_polygonscan_key(cls) -> bool:
        return bool(cls.POLYGONSCAN_API_KEY)

    @classmethod
    def any_api_key(cls) -> bool:
        return cls.has_etherscan_key() or cls.has_bscscan_key() or cls.has_polygonscan_key()
