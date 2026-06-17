import requests
from typing import Optional, Tuple, List, Dict

from .config import Config
from .cache import Cache
from .analyzer import TokenInfo, Holder, SampleGenerator


TOKEN_CONTRACTS = {
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "UNI": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "MATIC": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
    "SHIB": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
    "PEPE": "0x6982508145454Ce325dDbE47a25d4ec3d2311933",
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "CRO": "0xA0b73E1Ff0B80914AB6fe0444E65848C4C34450b",
}

EXPLORERS = {
    "etherscan": {
        "base": "https://api.etherscan.io/api",
        "key_env": "ETHERSCAN_API_KEY",
    },
    "bscscan": {
        "base": "https://api.bscscan.com/api",
        "key_env": "BSCSCAN_API_KEY",
    },
    "polygonscan": {
        "base": "https://api.polygonscan.com/api",
        "key_env": "POLYGONSCAN_API_KEY",
    },
}


def _get_explorer_for(symbol: str) -> str:
    matic_tokens = {"MATIC", "USDC", "USDT", "WETH", "LINK"}
    bsc_tokens = {"CRO"}
    if symbol in bsc_tokens:
        return "bscscan"
    if symbol in matic_tokens:
        return "polygonscan"
    return "etherscan"


class TokenFetcher:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.cache = Cache(self.config.CACHE_DIR, self.config.CACHE_TTL)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "TokenVision/1.0"})

    def fetch(self, symbol: str) -> Optional[Tuple[TokenInfo, List[Holder]]]:
        symbol = symbol.upper()
        contract = TOKEN_CONTRACTS.get(symbol)
        if not contract:
            return None

        cached = self.cache.get(f"holders_{symbol}")
        if cached:
            return self._from_cache(symbol, cached)

        if not self.config.any_api_key():
            return None

        try:
            explorer = _get_explorer_for(symbol)
            key = getattr(self.config, EXPLORERS[explorer]["key_env"], "")

            info = self._fetch_token_info(EXPLORERS[explorer]["base"], contract, key)
            if not info:
                return None

            holders_data = self._fetch_holders(EXPLORERS[explorer]["base"], contract, key)
            if holders_data:
                return self._process_data(symbol, info, holders_data)
        except Exception:
            return None

        return None

    def _fetch_token_info(self, base_url: str, contract: str, api_key: str) -> Optional[Dict]:
        params = {
            "module": "token",
            "action": "tokeninfo",
            "contractaddress": contract,
            "apikey": api_key,
        }
        try:
            resp = self.session.get(base_url, params=params, timeout=15)
            data = resp.json()
            if data.get("status") == "1" and data.get("result"):
                result = data["result"]
                divisor = int(result.get("divisor", "18"))
                total_supply_raw = float(result.get("totalSupply", 0))
                return {
                    "name": result.get("name", ""),
                    "decimals": divisor,
                    "total_supply": total_supply_raw / (10 ** divisor),
                }
        except Exception:
            pass
        return None

    def _fetch_holders(self, base_url: str, contract: str, api_key: str) -> Optional[List[Dict]]:
        params = {
            "module": "token",
            "action": "tokenholderlist",
            "contractaddress": contract,
            "apikey": api_key,
        }
        try:
            resp = self.session.get(base_url, params=params, timeout=30)
            data = resp.json()
            if data.get("status") == "1" and isinstance(data.get("result"), list):
                return data["result"][:100]
        except Exception:
            pass
        return None

    def _process_data(self, symbol: str, info: Dict, holders_data: List[Dict]) -> Tuple[TokenInfo, List[Holder]]:
        ti = TokenInfo(symbol, info["name"], info["decimals"], info["total_supply"])
        holders = []
        for h in holders_data:
            raw_bal = float(h.get("balance", 0))
            bal = raw_bal / (10 ** info["decimals"])
            pct = (bal / info["total_supply"]) * 100 if info["total_supply"] > 0 else 0
            holders.append(Holder(
                address=h.get("address", ""),
                balance=bal,
                percentage=pct,
                label="🐳 Mega Whale" if pct > 20 else "🐋 Whale" if pct > 10 else "🦈 Shark" if pct > 5 else "Whale" if pct > 3 else "",
            ))
        holders.sort(key=lambda h: h.balance, reverse=True)

        cache_payload = {
            "token": {"name": info["name"], "decimals": info["decimals"], "total_supply": info["total_supply"]},
            "holders": [{"address": h.address, "balance": h.balance, "percentage": h.percentage, "label": h.label} for h in holders],
        }
        self.cache.set(f"holders_{symbol}", cache_payload)
        return ti, holders[:100]

    def _from_cache(self, symbol: str, cached: dict) -> Tuple[TokenInfo, List[Holder]]:
        token_data = cached.get("token", {})
        ti = TokenInfo(
            symbol,
            token_data.get("name", symbol),
            token_data.get("decimals", 18),
            token_data.get("total_supply", 1_000_000_000),
        )
        holders = []
        for h in cached.get("holders", []):
            holders.append(Holder(
                address=h.get("address", ""),
                balance=h.get("balance", 0),
                percentage=h.get("percentage", 0),
                label=h.get("label", ""),
            ))
        if not holders:
            return SampleGenerator.generate(symbol)
        return ti, holders

    def get_token_contract(self, symbol: str) -> Optional[str]:
        return TOKEN_CONTRACTS.get(symbol.upper())
