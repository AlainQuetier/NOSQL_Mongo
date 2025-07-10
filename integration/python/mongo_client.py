"""
Client MongoDB pour l'intégration avec différents modes de déploiement.
"""
import os
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class MongoDBClient:
    """Client MongoDB avec support des différents modes de déploiement."""
    
    def __init__(self, connection_uri: str):
        """
        Initialise le client MongoDB.
        
        Args:
            connection_uri: URI de connexion MongoDB
                - Standalone: mongodb://user:pass@host:port/database
                - Replica Set: mongodb://user:pass@host1:port1,host2:port2/database?replicaSet=rs0
                - Sharding: mongodb://user:pass@mongos_host:port/database
        """
        self.uri = connection_uri
        self.client = None
        self.db = None
        
    def connect(self) -> bool:
        """
        Établit la connexion à MongoDB.
        
        Returns:
            bool: True si la connexion est réussie, False sinon
        """
        try:
            # Connexion avec timeout
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            
            # Test de connexion
            self.client.admin.command('ping')
            
            # Récupération de la base depuis l'URI
            db_name = self.uri.split('/')[-1].split('?')[0]
            self.db = self.client[db_name]
            
            print(f"Connexion réussie à MongoDB ({db_name})")
            return True
            
        except ConnectionFailure as e:
            print(f"Erreur de connexion: {e}")
            return False
        except Exception as e:
            print(f"Erreur: {e}")
            return False
    
    def get_server_info(self) -> Dict:
        """
        Récupère les informations du serveur MongoDB.
        
        Returns:
            Dict: Informations du serveur
        """
        if not self.client:
            return {}
            
        try:
            info = self.client.server_info()
            return {
                'version': info.get('version'),
                'gitVersion': info.get('gitVersion'),
                'maxBsonObjectSize': info.get('maxBsonObjectSize'),
                'maxMessageSizeBytes': info.get('maxMessageSizeBytes')
            }
        except Exception as e:
            print(f"Erreur lors de la récupération des infos serveur: {e}")
            return {}
    
    def get_replica_set_status(self) -> Optional[Dict]:
        """
        Récupère le statut du replica set (si applicable).
        
        Returns:
            Dict: Statut du replica set ou None
        """
        if not self.client:
            return None
            
        try:
            status = self.client.admin.command('replSetGetStatus')
            return {
                'set': status.get('set'),
                'members': [{
                    'name': member.get('name'),
                    'stateStr': member.get('stateStr'),
                    'health': member.get('health')
                } for member in status.get('members', [])]
            }
        except OperationFailure:
            # Pas un replica set
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération du statut replica set: {e}")
            return None
    
    def insert_document(self, collection_name: str, document: Dict) -> Optional[str]:
        """
        Insère un document dans une collection.
        
        Args:
            collection_name: Nom de la collection
            document: Document à insérer
            
        Returns:
            str: ID du document inséré ou None
        """
        if not self.db:
            print("Pas de connexion à la base de données")
            return None
            
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(document)
            print(f"Document inséré avec l'ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"Erreur lors de l'insertion: {e}")
            return None
    
    def find_documents(self, collection_name: str, filter_dict: Dict = None, limit: int = 10) -> List[Dict]:
        """
        Recherche des documents dans une collection.
        
        Args:
            collection_name: Nom de la collection
            filter_dict: Filtre de recherche (optionnel)
            limit: Limite de résultats
            
        Returns:
            List[Dict]: Liste des documents trouvés
        """
        if not self.db:
            print("Pas de connexion à la base de données")
            return []
            
        try:
            collection = self.db[collection_name]
            filter_dict = filter_dict or {}
            
            cursor = collection.find(filter_dict).limit(limit)
            documents = list(cursor)
            
            print(f"{len(documents)} document(s) trouvé(s)")
            return documents
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return []
    
    def update_document(self, collection_name: str, filter_dict: Dict, update_dict: Dict) -> int:
        """
        Met à jour un document dans une collection.
        
        Args:
            collection_name: Nom de la collection
            filter_dict: Filtre pour identifier le document
            update_dict: Données de mise à jour
            
        Returns:
            int: Nombre de documents modifiés
        """
        if not self.db:
            print("Pas de connexion à la base de données")
            return 0
            
        try:
            collection = self.db[collection_name]
            result = collection.update_many(filter_dict, {'$set': update_dict})
            print(f"{result.modified_count} document(s) mis à jour")
            return result.modified_count
        except Exception as e:
            print(f"Erreur lors de la mise à jour: {e}")
            return 0
    
    def delete_documents(self, collection_name: str, filter_dict: Dict) -> int:
        """
        Supprime des documents d'une collection.
        
        Args:
            collection_name: Nom de la collection
            filter_dict: Filtre pour identifier les documents
            
        Returns:
            int: Nombre de documents supprimés
        """
        if not self.db:
            print("Pas de connexion à la base de données")
            return 0
            
        try:
            collection = self.db[collection_name]
            result = collection.delete_many(filter_dict)
            print(f"{result.deleted_count} document(s) supprimé(s)")
            return result.deleted_count
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
            return 0
    
    def close(self):
        """Ferme la connexion MongoDB."""
        if self.client:
            self.client.close()
            print("Connexion fermée")


def test_standalone():
    """Test avec MongoDB standalone."""
    print("\n=== Test MongoDB Standalone ===")
    
    uri = os.getenv('MONGO_STANDALONE_URI', 'mongodb://testuser:testpass@localhost:27017/testdb')
    client = MongoDBClient(uri)
    
    if client.connect():
        # Informations serveur
        info = client.get_server_info()
        print(f"Version MongoDB: {info.get('version', 'N/A')}")
        
        # Test des opérations CRUD
        doc_id = client.insert_document('test_app', {
            'name': 'Test depuis Python',
            'type': 'application',
            'value': 42,
            'created': datetime.now()
        })
        
        # Recherche
        docs = client.find_documents('test_app', {'type': 'application'})
        for doc in docs:
            print(f"Document trouvé: {doc}")
        
        # Mise à jour
        client.update_document('test_app', {'name': 'Test depuis Python'}, {'value': 84})
        
        # Suppression
        client.delete_documents('test_app', {'name': 'Test depuis Python'})
        
        client.close()


def test_replica_set():
    """Test avec MongoDB replica set."""
    print("\n=== Test MongoDB Replica Set ===")
    
    uri = os.getenv('MONGO_REPLICA_URI', 
                   'mongodb://testuser:testpass@localhost:27018,localhost:27019,localhost:27020/testdb?replicaSet=rs0')
    client = MongoDBClient(uri)
    
    if client.connect():
        # Informations serveur
        info = client.get_server_info()
        print(f"Version MongoDB: {info.get('version', 'N/A')}")
        
        # Statut replica set
        rs_status = client.get_replica_set_status()
        if rs_status:
            print(f"Replica Set: {rs_status['set']}")
            for member in rs_status['members']:
                print(f"  - {member['name']}: {member['stateStr']}")
        
        # Test des opérations CRUD
        doc_id = client.insert_document('test_app', {
            'name': 'Test RS depuis Python',
            'type': 'replica-set',
            'value': 123,
            'created': datetime.now()
        })
        
        # Recherche
        docs = client.find_documents('test_app', {'type': 'replica-set'})
        for doc in docs:
            print(f"Document trouvé: {doc}")
        
        client.close()


if __name__ == "__main__":
    test_standalone()
    test_replica_set()
