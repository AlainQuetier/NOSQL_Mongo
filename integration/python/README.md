## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copier le fichier `.env.example` vers `.env`:
```bash
cp .env.example .env
```

2. Adapter les URIs de connexion selon votre configuration

## Utilisation

### Test des connexions

```bash
python mongo_client.py
```

### Lancement des tests

```bash
python -m pytest tests/ -v
```

## Méthodes de connexion

### 1. MongoDB Standalone
```python
# URI simple
uri = "mongodb://testuser:testpass@localhost:27017/testdb"

# Avec options
uri = "mongodb://testuser:testpass@localhost:27017/testdb?authSource=testdb"
```

### 2. MongoDB Replica Set
```python
# URI avec replica set
uri = "mongodb://testuser:testpass@localhost:27018,localhost:27019,localhost:27020/testdb?replicaSet=rs0"

# Avec préférence de lecture
uri = "mongodb://testuser:testpass@localhost:27018,localhost:27019,localhost:27020/testdb?replicaSet=rs0&readPreference=secondary"
```

### 3. MongoDB Sharding
```python
# URI vers mongos
uri = "mongodb://testuser:testpass@localhost:27021/sharddb"
```

## Opérations supportées

1. **Connexion sécurisée** - Authentification et test de connexion
2. **Insertion** - Ajout de documents avec validation
3. **Recherche** - Requêtes avec filtres et pagination
4. **Mise à jour** - Modification de documents existants
5. **Suppression** - Suppression conditionnelle
6. **Informations serveur** - Récupération des métadonnées
7. **Statut replica set** - Monitoring des membres (si applicable)

## Exemples d'utilisation

```python
from mongo_client import MongoDBClient

# Connexion
client = MongoDBClient("mongodb://testuser:testpass@localhost:27017/testdb")
client.connect()

# Insertion
doc_id = client.insert_document('ma_collection', {
    'nom': 'Test',
    'valeur': 42
})

# Recherche
docs = client.find_documents('ma_collection', {'nom': 'Test'})

# Mise à jour
client.update_document('ma_collection', {'nom': 'Test'}, {'valeur': 84})

# Suppression
client.delete_documents('ma_collection', {'nom': 'Test'})

# Fermeture
client.close()
```
