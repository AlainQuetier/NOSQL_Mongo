# MongoDB Replica Set

Déploiement MongoDB en replica set avec 3 membres pour la haute disponibilité.

## Architecture

- **mongo1** (PRIMARY) - Port 27018
- **mongo2** (SECONDARY) - Port 27019  
- **mongo3** (SECONDARY) - Port 27020

## Démarrage

```bash
docker-compose up -d
```

L'initialisation du replica set se fait automatiquement via le container `mongo-rs-init`.

## Connexion

### Connexion au replica set complet
```bash
mongosh "mongodb://admin:password123@localhost:27018,localhost:27019,localhost:27020/admin?replicaSet=rs0"
```

### Connexion avec utilisateur testuser
```bash
mongosh "mongodb://testuser:testpass@localhost:27018,localhost:27019,localhost:27020/testdb?replicaSet=rs0"
```

### Connexion à un membre spécifique
```bash
# PRIMARY
mongosh mongodb://admin:password123@localhost:27018/admin

# SECONDARY
mongosh mongodb://admin:password123@localhost:27019/admin
```

## Commandes de test

```javascript
// Vérifier le statut du replica set
rs.status()

// Voir la configuration
rs.conf()

// Qui est le PRIMARY
rs.isMaster()

// Utilisation de la base testdb
use testdb

// Lire depuis le PRIMARY
db.test.find()

// Pour lire depuis un SECONDARY
db.getMongo().setReadPref('secondary')
db.test.find()

// Tester la réplication
// Sur le PRIMARY
db.test.insertOne({
  name: 'Test réplication',
  type: 'replication-test',
  value: 9999,
  created: new Date()
})

// Sur un SECONDARY (avec readPreference)
db.getMongo().setReadPref('secondary')
db.test.find({type: 'replication-test'})
```

## Modes de lecture

```javascript
// Lecture depuis le PRIMARY uniquement (par défaut)
db.getMongo().setReadPref('primary')

// Lecture depuis un SECONDARY si possible
db.getMongo().setReadPref('secondary')

// Lecture depuis PRIMARY ou SECONDARY
db.getMongo().setReadPref('primaryPreferred')
db.getMongo().setReadPref('secondaryPreferred')
```

## Arrêt

```bash
docker-compose down
```