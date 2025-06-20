from logging.handlers import RotatingFileHandler
from datetime import datetime
from app.core.config import Config
import logging, os, sys

class NewLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        self.logger = logging.getLogger(Config.APP_NAME)
        self.logger.setLevel(Config.LOG_LEVEL)
        
        formatter = logging.Formatter(
            Config.LOG_FORMAT
        )
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)
            
        log_file = os.path.join(
            logs_dir, 
            f"app_{datetime.now().strftime('%Y-%m-%d')}.log"
        )
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message):
        self.logger.info(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def debug(self, message):
        self.logger.debug(message) 


Logger = NewLogger()