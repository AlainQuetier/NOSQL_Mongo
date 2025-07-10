"""
Tests pour les opérations MongoDB.
"""
import unittest
from datetime import datetime
from integration.python.mongo_client import MongoDBClient


class TestMongoOperations(unittest.TestCase):
    """Tests des opérations MongoDB."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.uri = 'mongodb://testuser:testpass@localhost:27017/testdb'
        self.client = MongoDBClient(self.uri)
        self.client.connect()
        
        # Nettoyer la collection de test
        if self.client.db:
            self.client.db['test_operations'].delete_many({})
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        if self.client.db:
            self.client.db['test_operations'].delete_many({})
        self.client.close()
    
    def test_insert_document(self):
        """Test d'insertion de document."""
        document = {
            'name': 'Test Insert',
            'value': 100,
            'created': datetime.now()
        }
        
        doc_id = self.client.insert_document('test_operations', document)
        self.assertIsNotNone(doc_id)
        
        # Vérifier que le document a été inséré
        docs = self.client.find_documents('test_operations', {'name': 'Test Insert'})
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['value'], 100)
    
    def test_find_documents(self):
        """Test de recherche de documents."""
        # Insérer des documents de test
        documents = [
            {'name': 'Doc1', 'type': 'test', 'value': 10},
            {'name': 'Doc2', 'type': 'test', 'value': 20},
            {'name': 'Doc3', 'type': 'other', 'value': 30}
        ]
        
        for doc in documents:
            self.client.insert_document('test_operations', doc)
        
        # Test recherche sans filtre
        all_docs = self.client.find_documents('test_operations')
        self.assertEqual(len(all_docs), 3)
        
        # Test recherche avec filtre
        test_docs = self.client.find_documents('test_operations', {'type': 'test'})
        self.assertEqual(len(test_docs), 2)
        
        # Test recherche avec limite
        limited_docs = self.client.find_documents('test_operations', {}, limit=2)
        self.assertEqual(len(limited_docs), 2)
    
    def test_update_document(self):
        """Test de mise à jour de document."""
        # Insérer un document
        document = {'name': 'Test Update', 'value': 50}
        self.client.insert_document('test_operations', document)
        
        # Mettre à jour
        updated_count = self.client.update_document(
            'test_operations',
            {'name': 'Test Update'},
            {'value': 75, 'updated': True}
        )
        
        self.assertEqual(updated_count, 1)
        
        # Vérifier la mise à jour
        docs = self.client.find_documents('test_operations', {'name': 'Test Update'})
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['value'], 75)
        self.assertTrue(docs[0]['updated'])
    
    def test_delete_documents(self):
        """Test de suppression de documents."""
        # Insérer des documents
        documents = [
            {'name': 'ToDelete1', 'type': 'delete'},
            {'name': 'ToDelete2', 'type': 'delete'},
            {'name': 'ToKeep', 'type': 'keep'}
        ]
        
        for doc in documents:
            self.client.insert_document('test_operations', doc)
        
        # Supprimer les documents de type 'delete'
        deleted_count = self.client.delete_documents('test_operations', {'type': 'delete'})
        self.assertEqual(deleted_count, 2)
        
        # Vérifier qu'il reste seulement le document 'keep'
        remaining_docs = self.client.find_documents('test_operations')
        self.assertEqual(len(remaining_docs), 1)
        self.assertEqual(remaining_docs[0]['type'], 'keep')
    
    def test_connection_failure(self):
        """Test de gestion d'erreur de connexion."""
        bad_client = MongoDBClient('mongodb://baduser:badpass@localhost:27017/testdb')
        self.assertFalse(bad_client.connect())


if __name__ == '__main__':
    unittest.main()