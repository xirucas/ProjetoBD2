from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

class MongoDBManager:
    """
    Classe para gerenciar conexões e operações com MongoDB
    """
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Conecta ao MongoDB"""
        try:
            mongodb_settings = getattr(settings, 'MONGODB_SETTINGS', {})
            url = mongodb_settings.get('url', 'mongodb://localhost:27017/')
            db_name = mongodb_settings.get('db', 'ProjetoBD2')
            
            self._client = MongoClient(url, serverSelectionTimeoutMS=5000)
            # Testa a conexão
            self._client.admin.command('ping')
            self._db = self._client[db_name]
            logger.info(f"MongoDB connected successfully to {db_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._client = None
            self._db = None
    
    def get_database(self):
        """Retorna a instância do banco MongoDB"""
        if self._db is None:
            self.connect()
        return self._db
    
    def get_collection(self, collection_name):
        """Retorna uma coleção específica"""
        db = self.get_database()
        if db is not None:
            return db[collection_name]
        return None
    
    def is_connected(self):
        """Verifica se está conectado ao MongoDB"""
        return self._db is not None

# Instância global do gerenciador MongoDB
mongo_manager = MongoDBManager()