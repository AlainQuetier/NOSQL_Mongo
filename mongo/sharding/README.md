# MongoDB Sharding

Déploiement MongoDB avec sharding pour la distribution horizontale des données.

## Architecture

### Config Servers (Replica Set)
- **configsvr1** - Port 27030
- **configsvr2** - Port 27031
- **configsvr3** - Port 27032

### Shards
- **shard1** - Port 27040
- **shard2** - Port 27041
- **shard3** - Port 27042

### Mongos Router
- **mongos** - Port 27021

## Démarrage

```bash
docker-compose up -d
```

L'initialisation du sharding se fait automatiquement via le container `mongo-shard-init`.

## Connexion

### Connexion au mongos (recommandé)
```bash
mongosh mongodb://admin:password123@localhost:27021/admin
```

### Connexion avec utilisateur testuser
```bash
mongosh mongodb://testuser:testpass@localhost:27021/sharddb
```

## Commandes de test

```javascript
// Statut du sharding
sh.status()

// Informations sur les shards
sh.getShards()

// Utilisation de la base sharddb
use sharddb

// Voir les données distribuées
db.products.find().limit(10)

// Statistiques par shard
db.products.getShardDistribution()

// Compter les documents par catégorie
db.products.aggregate([
  {$group: {_id: "$category", count: {$sum: 1}}}
])

// Voir la répartition des chunks
sh.status()

// Insérer plus de données pour forcer le balancing
for (let i = 1000; i < 2000; i++) {
  db.products.insertOne({
    _id: i,
    name: `Product ${i}`,
    category: 'new_category',
    price: Math.floor(Math.random() * 1000) + 1,
    stock: Math.floor(Math.random() * 100) + 1,
    created: new Date()
  })
}

// Forcer le balancing
sh.startBalancer()
sh.getBalancerState()
```

## Clé de sharding

La collection `products` est shardée sur `{category: 1, _id: 1}` :
- **category** : Assure une distribution équilibrée des données
- **_id** : Garantit l'unicité et évite les hotspots

## Avantages de cette clé

1. **Distribution équilibrée** : Les catégories sont réparties sur les shards
2. **Évitement des hotspots** : L'ajout de _id évite la concentration sur un shard
3. **Requêtes efficaces** : Les requêtes par catégorie sont dirigées vers les bons shards

## Monitoring

```javascript
// Statut des shards
sh.status()

// État du balancer
sh.getBalancerState()

// Statistiques de la collection
db.products.stats()

// Répartition par shard
db.products.getShardDistribution()
```

## Connexion directe aux shards (debug)

```bash
# Shard 1
mongosh mongodb://localhost:27040/admin

# Shard 2  
mongosh mongodb://localhost:27041/admin

# Shard 3
mongosh mongodb://localhost:27042/admin
```

## Arrêt

```bash
docker-compose down
```