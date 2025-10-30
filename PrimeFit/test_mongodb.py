"""
Teste de conexão MongoDB
Execute este arquivo para testar a conexão com MongoDB Atlas
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório do projeto ao Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configura as variáveis de ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrimeFit.settings')

import django
django.setup()

from PrimeFit.mongodb_manager import mongo_manager

def test_mongodb_connection():
    print("Testando conexão com MongoDB...")
    
    if mongo_manager.is_connected():
        print("✅ MongoDB conectado com sucesso!")
        
        # Testa inserção de um documento
        db = mongo_manager.get_database()
        test_collection = db['test_collection']
        
        # Insere um documento de teste
        test_doc = {"test": "connection", "timestamp": "2025-10-30"}
        result = test_collection.insert_one(test_doc)
        
        print(f"✅ Documento de teste inserido: {result.inserted_id}")
        
        # Lista as coleções existentes
        collections = db.list_collection_names()
        print(f"📁 Coleções existentes: {collections}")
        
        # Remove o documento de teste
        test_collection.delete_one({"_id": result.inserted_id})
        print("🗑️ Documento de teste removido")
        
    else:
        print("❌ Falha na conexão com MongoDB")
        print("Verifique se:")
        print("1. As credenciais no .env estão corretas")
        print("2. A URL do MongoDB Atlas está correta")
        print("3. O IP está na whitelist do MongoDB Atlas")

if __name__ == "__main__":
    test_mongodb_connection()