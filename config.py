"""
ACATN Configuration Manager
Centralized configuration with environment variable support and validation
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

@dataclass
class FirebaseConfig:
    """Firebase configuration with validation"""
    type: str = os.getenv("FIREBASE_TYPE", "")
    project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    private_key_id: str = os.getenv("FIREBASE_PRIVATE_KEY_ID", "")
    private_key: str = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')
    client_email: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    client_id: str = os.getenv("FIREBASE_CLIENT_ID", "")
    auth_uri: str = os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
    token_uri: str = os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token")
    auth_provider_x509_cert_url: str = os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL", 
                                                "https://www.googleapis.com/oauth2/v1/certs")
    client_x509_cert_url: str = os.getenv("FIREBASE_CLIENT_CERT_URL", "")
    
    def validate(self) -> bool:
        """Validate Firebase configuration"""
        required_fields = ['project_id', 'private_key', 'client_email']
        missing = [field for field in required_fields if not getattr(self, field)]
        
        if missing:
            logger.error(f"Missing Firebase config fields: {missing}")
            return False
        
        if not self.private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            logger.error("Firebase private key format invalid")
            return False
            
        return True

@dataclass
class TradingConfig:
    """Trading parameters and limits"""
    # Risk Management
    max_position_size: float = float(os.getenv("MAX_POSITION_SIZE", "0.1"))  # 10% of portfolio
    max_daily_loss: float = float(os.getenv("MAX_DAILY_LOSS", "0.02"))  # 2% daily loss limit
    max_correlation_threshold: float = float(os.getenv("MAX_CORRELATION", "0.8"))
    min_volatility_threshold: float = float(os.getenv("MIN_VOLATILITY", "0.005"))
    
    # Asset Classes
    crypto_symbols: list = None
    stock_symbols: list = None
    commodity_symbols: list = None
    
    # Data Settings
    historical_days: int = int(os.getenv("HISTORICAL_DAYS", "365"))
    data_update_interval: int = int(os.getenv("DATA_UPDATE_INTERVAL", "300"))  # 5 minutes
    
    def __post_init__(self):
        """Initialize default symbols"""
        if self.crypto_symbols is None:
            self.crypto_symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        if self.stock_symbols is None:
            self.stock_symbols = ['AAPL', 'MSFT', 'GOOGL']
        if self.commodity_symbols is None:
            self.commodity_symbols = ['GC=F', 'SI=F', 'CL=F']  # Gold, Silver, Oil futures

@dataclass
class RLConfig:
    """Reinforcement Learning configuration"""
    learning_rate: float = float(os.getenv("RL_LEARNING_RATE", "0.001"))
    gamma: float = float(os.getenv("RL_GAMMA", "0.99"))
    epsilon_start: float = float(os.getenv("RL_EPSILON_START", "1.0"))
    epsilon_end: float = float(os.getenv("RL_EPSILON_END", "0.01"))
    epsilon_decay: float = float(os.getenv("RL_EPSILON_DECAY", "0.995"))
    replay_buffer_size: int = int(os.getenv("REPLAY_BUFFER_SIZE", "10000"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "64"))
    target_update_frequency: int = int(os.getenv("TARGET_UPDATE_FREQ", "10"))

class ConfigManager:
    """Singleton configuration manager"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize all configurations"""
        try:
            self.firebase = FirebaseConfig()
            self.trading = TradingConfig()
            self.rl = RLConfig()
            
            # Validate critical configs
            if not self.firebase.validate():
                logger.warning("Firebase config validation failed - proceeding without Firebase")
            
            logger.success("Configuration initialized successfully")
            
        except Exception as e:
            logger.error(f"Configuration initialization failed: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization"""
        return {
            'firebase': asdict(self.firebase),
            'trading': asdict(self.trading),
            'rl': asdict(self.rl)
        }
    
    def save_to_firebase(self):
        """Save configuration to Firebase (when available)"""
        # Implementation depends on Firebase setup
        pass

# Global config instance
config = ConfigManager()