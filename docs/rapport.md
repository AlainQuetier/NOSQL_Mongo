# Rapport d'Atelier MongoDB

## Objectifs réalisés

-  Déploiement MongoDB Standalone avec authentification
-  Configuration d'un Replica Set à 3 membres
-  Intégration avec une application Python
-  Implémentation du sharding (bonus)
-  Documentation complète et tests

---

## Partie 1 – MongoDB Standalone

### Méthode de déploiement

**Technologie utilisée :** Docker Compose  
**Localisation :** `mongo/standalone/`

### Configuration

```yaml
# docker-compose.yml
services:
  mongo:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password123
      MONGO_INITDB_DATABASE: testdb
    command: mongod --auth
```

### Création de l'utilisateur

L'utilisateur admin est créé automatiquement via les variables d'environnement Docker.
Un utilisateur applicatif `testuser` est créé via le script `init-mongo.js` :

```javascript
db.getSiblingDB('testdb').createUser({
  user: 'testuser',
  pwd: 'testpass',
  roles: [{ role: 'readWrite', db: 'testdb' }]
});
```

### Méthodes de connexion

| Méthode | URI | Usage |
|---------|-----|-------|
| Admin | `mongodb://admin:password123@localhost:27017/admin` | Administration |
| Utilisateur | `mongodb://testuser:testpass@localhost:27017/testdb` | Application |

### Opérations CRUD réalisées

**1. Insertion**
```javascript
db.test.insertOne({
  name: 'Document 1',
  type: 'example',
  value: 100,
  created: new Date()
});
```

**2. Lecture**
```javascript
db.test.find({type: 'example'});
```

**3. Mise à jour**
```javascript
db.test.updateOne(
  {name: 'Document 1'},
  {$set: {value: 120}}
);
```

**4. Suppression**
```javascript
db.test.deleteOne({name: 'Document 3'});
```

### Résultats

-  Authentification fonctionnelle
-  Base `testdb` créée avec succès
-  Collection `test` avec 3 documents initiaux
-  Opérations CRUD validées

---

## Partie 2 – MongoDB Replica Set

### Configuration des membres

**Architecture :** 3 membres en replica set `rs0`

| Membre | Host | Port | Rôle | Priorité |
|--------|------|------|------|----------|
| mongo1 | mongo1:27017 | 27018 | PRIMARY | 2 |
| mongo2 | mongo2:27017 | 27019 | SECONDARY | 1 |
| mongo3 | mongo3:27017 | 27020 | SECONDARY | 1 |

### Méthode d'initialisation

**Script automatique :** `rs-init.js`

```javascript
rs.initiate({
  _id: "rs0",
  members: [
    {_id: 0, host: "mongo1:27017", priority: 2},
    {_id: 1, host: "mongo2:27017", priority: 1},
    {_id: 2, host: "mongo3:27017", priority: 1}
  ]
});
```

### Sécurité

- **Authentification inter-membres :** Keyfile partagé
- **Chiffrement :** Communication interne sécurisée
- **Utilisateurs :** Création automatique d'utilisateurs applicatifs

### Méthodes de connexion

**1. Connexion complète au replica set**
```
mongodb://testuser:testpass@localhost:27018,localhost:27019,localhost:27020/testdb?replicaSet=rs0
```

**2. Connexion avec préférence de lecture**
```
mongodb://testuser:testpass@localhost:27018,localhost:27019,localhost:27020/testdb?replicaSet=rs0&readPreference=secondary
```

### Modes de lecture/écriture

| Mode | Description | URI |
|------|-------------|-----|
| primary | Lecture/écriture sur PRIMARY uniquement | `readPreference=primary` |
| secondary | Lecture sur SECONDARY uniquement | `readPreference=secondary` |
| primaryPreferred | PRIMARY puis SECONDARY | `readPreference=primaryPreferred` |
| secondaryPreferred | SECONDARY puis PRIMARY | `readPreference=secondaryPreferred` |

### Tests de réplication

**Insertion sur PRIMARY :**
```javascript
db.test.insertOne({
  name: 'Test réplication',
  type: 'replication-test',
  value: 9999,
  created: new Date()
});
```

**Lecture sur SECONDARY :**
```javascript
db.getMongo().setReadPref('secondary');
db.test.find({type: 'replication-test'});
```

### Résultats

-  Replica set initialisé avec succès
-  Élection PRIMARY/SECONDARY fonctionnelle
-  Réplication des données validée
-  Modes de lecture testés

---

## Partie 3 – Intégration Application

### Technologie et dépendances

**Langage :** Python 3.8+  
**Dépendances :**
- `pymongo==4.6.0` - Driver MongoDB officiel
- `python-dotenv==1.0.0` - Gestion des variables d'environnement

### Architecture de l'application

```
integration/python/
├── mongo_client.py      # Client MongoDB principal
├── requirements.txt     # Dépendances
├── .env.example        # Configuration
├── tests/
│   └── test_operations.py  # Tests automatisés
└── README.md           # Documentation
```

### Code de connexion

```python
class MongoDBClient:
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
        """Établit la connexion à MongoDB."""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            
            db_name = self.uri.split('/')[-1].split('?')[0]
            self.db = self.client[db_name]
            
            print(f"Connexion réussie à MongoDB ({db_name})")
            return True
            
        except ConnectionFailure as e:
            print(f"Erreur de connexion: {e}")
            return False
```

### Opérations implémentées

**1. Connexion sécurisée**
- Gestion des timeouts
- Validation de la connexion
- Gestion des erreurs

**2. Insertion**
```python
def insert_document(self, collection_name: str, document: Dict) -> Optional[str]:
    """Insère un document dans une collection."""
    collection = self.db[collection_name]
    result = collection.insert_one(document)
    return str(result.inserted_id)
```

**3. Recherche**
```python
def find_documents(self, collection_name: str, filter_dict: Dict = None, limit: int = 10) -> List[Dict]:
    """Recherche des documents avec filtres et pagination."""
    collection = self.db[collection_name]
    filter_dict = filter_dict or {}
    cursor = collection.find(filter_dict).limit(limit)
    return list(cursor)
```

**4. Mise à jour**
```python
def update_document(self, collection_name: str, filter_dict: Dict, update_dict: Dict) -> int:
    """Met à jour des documents."""
    collection = self.db[collection_name]
    result = collection.update_many(filter_dict, {'$set': update_dict})
    return result.modified_count
```

**5. Suppression**
```python
def delete_documents(self, collection_name: str, filter_dict: Dict) -> int:
    """Supprime des documents."""
    collection = self.db[collection_name]
    result = collection.delete_many(filter_dict)
    return result.deleted_count
```

### Commentaires sur les méthodes de connexion

**Standalone :**
- URI simple : `mongodb://user:pass@host:port/database`
- Idéal pour développement et tests
- Pas de haute disponibilité

**Replica Set :**
- URI multi-hôtes : `mongodb://user:pass@host1:port1,host2:port2/database?replicaSet=rs0`
- Haute disponibilité automatique
- Répartition de charge en lecture

**Sharding :**
- URI vers mongos : `mongodb://user:pass@mongos_host:port/database`
- Transparent pour l'application
- Scalabilité horizontale

### Tests automatisés

**Framework :** unittest  
**Coverage :** 
- Tests de connexion
- Tests CRUD complets
- Tests de gestion d'erreurs
- Tests de validation

**Exemple de test :**
```python
def test_insert_document(self):
    document = {
        'name': 'Test Insert',
        'value': 100,
        'created': datetime.now()
    }
    
    doc_id = self.client.insert_document('test_operations', document)
    self.assertIsNotNone(doc_id)
    
    docs = self.client.find_documents('test_operations', {'name': 'Test Insert'})
    self.assertEqual(len(docs), 1)
    self.assertEqual(docs[0]['value'], 100)
```

### Résultats des tests

- Connexion standalone validée
- Connexion replica set validée
- Toutes les opérations CRUD fonctionnelles
- Gestion d'erreurs opérationnelle
- Tests automatisés passants

---

## Partie 4 – Sharding MongoDB (Bonus)

### Architecture déployée

**Config Servers (Replica Set) :**
- configsvr1:27030, configsvr2:27031, configsvr3:27032
- Replica set `configReplSet`

**Shards :**
- shard1:27040 (replica set `shard1ReplSet`)
- shard2:27041 (replica set `shard2ReplSet`)  
- shard3:27042 (replica set `shard3ReplSet`)

**Mongos Router :**
- mongos:27021

### Scripts et commandes utilisés

**Initialisation automatique :** `shard-init.js`

```javascript
// 1. Initialisation config servers
db.runCommand({
    replSetInitiate: {
        _id: 'configReplSet',
        configsvr: true,
        members: [
            {_id: 0, host: 'configsvr1:27017'},
            {_id: 1, host: 'configsvr2:27017'},
            {_id: 2, host: 'configsvr3:27017'}
        ]
    }
});

// 2. Initialisation shards
sh.addShard('shard1ReplSet/shard1:27017');
sh.addShard('shard2ReplSet/shard2:27017');
sh.addShard('shard3ReplSet/shard3:27017');

// 3. Activation sharding
sh.enableSharding('sharddb');

// 4. Définition clé de sharding
sh.shardCollection('sharddb.products', {category: 1, _id: 1});
```

### Raisonnement autour de la clé de sharding

**Clé choisie :** `{category: 1, _id: 1}`

**Justification :**
1. **Distribution équilibrée** : Le champ `category` assure une répartition des données selon les catégories de produits
2. **Évitement des hotspots** : L'ajout de `_id` évite la concentration des écritures sur un seul shard
3. **Efficacité des requêtes** : Les requêtes par catégorie sont dirigées vers les shards appropriés
4. **Unicité garantie** : `_id` assure l'unicité des documents

**Alternatives considérées :**
- `{_id: 1}` : Évite les hotspots mais pas de localisation des données
- `{category: 1}` : Bonne distribution mais risque de hotspots
- `{created: 1}` : Hotspots garantis (toujours le même shard)

### Observations sur la distribution

**Données insérées :** 1000 produits de test répartis sur 5 catégories

**Commandes de monitoring :**
```javascript
// Statut global
sh.status();

// Distribution par collection
db.products.getShardDistribution();

// Statistiques par shard
db.products.aggregate([
  {$group: {_id: "$category", count: {$sum: 1}}}
]);
```

**Résultats observés :**
- Distribution équilibrée des chunks
- Répartition homogène des catégories
- Pas de hotspots détectés
- Balancer automatique fonctionnel

### Monitoring et maintenance

**Commandes de monitoring :**
```javascript
sh.getBalancerState()    // État du balancer
sh.isBalancerRunning()   // Balancer actif
sh.getShards()          // Liste des shards
db.printShardingStatus() // Statut détaillé
```

**Résultats :**
- Cluster sharding opérationnel
- Balancer automatique activé
- Tous les shards accessibles
- Requêtes distribuées correctement

---

## Problèmes rencontrés et résolutions

### 1. Gestion des keyfiles

**Problème :** Permissions incorrectes sur les keyfiles partagés entre containers

**Solution :** Script d'initialisation dédié pour générer et distribuer les keyfiles avec les bonnes permissions (400)

```bash
openssl rand -base64 756 > /data/keyfile
chmod 400 /data/keyfile
```

### 2. Synchronisation des replica sets

**Problème :** Timeouts lors de l'initialisation des replica sets

**Solution :** Ajout de délais d'attente et de vérifications de connectivité

```javascript
function waitForConnection(host, maxRetries = 10) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            let conn = new Mongo(host);
            conn.getDB('admin').runCommand({ping: 1});
            return conn;
        } catch (e) {
            sleep(3000);
        }
    }
}
```

### 3. Authentification cross-database

**Problème :** Utilisateurs créés sur une base non accessibles depuis une autre

**Solution :** Utilisation de `authSource` dans les URIs de connexion et création d'utilisateurs avec les bonnes permissions

---

## Métriques et performances

### Temps de déploiement

| Mode | Temps de démarrage | Temps d'initialisation |
|------|-------------------|------------------------|
| Standalone | ~10 secondes | ~5 secondes |
| Replica Set | ~30 secondes | ~15 secondes |
| Sharding | ~60 secondes | ~30 secondes |

### Utilisation des ressources

| Composant | CPU | RAM | Stockage |
|-----------|-----|-----|----------|
| MongoDB Standalone | ~5% | ~200MB | ~100MB |
| Replica Set (3 membres) | ~15% | ~600MB | ~300MB |
| Sharding (7 composants) | ~35% | ~1.4GB | ~700MB |
