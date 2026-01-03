import json
import os
from typing import Dict, Optional
from app.utils.logger import get_logger

logger = get_logger("config")

# Cache for loaded configs
_config_cache: Dict[str, Dict] = {}


def load_org_config(org_name: str = "sample_org", path: Optional[str] = None) -> Dict:
    """Load organization config JSON.
    
    Args:
        org_name: Organization identifier (defaults to sample_org)
        path: Optional explicit path to config.json
    
    Returns:
        Dict with organization configuration
    """
    # Check cache
    if org_name in _config_cache:
        return _config_cache[org_name]
    
    # Build path if not provided
    if path is None:
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        path = os.path.join(base, "data", org_name, "config.json")
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Cache the config
        _config_cache[org_name] = config
        logger.info(f"Loaded config for {org_name}")
        
        return config
    
    except FileNotFoundError:
        logger.error(f"Config file not found: {path}")
        # Return default config
        return {
            "org_name": org_name,
            "assistant_role": "AI Assistant",
            "language": "English",
            "tone": "polite",
            "knowledge_path": f"data/{org_name}/knowledge/"
        }
    
    except Exception as e:
        logger.exception(f"Error loading config: {e}")
        return {}


def get_org_from_phone(phone_number: str) -> str:
    """Map phone number to organization name.
    
    Args:
        phone_number: Twilio phone number
    
    Returns:
        Organization identifier
    """
    # TODO: Implement phone number to org mapping
    # For now, return default
    return "sample_org"
