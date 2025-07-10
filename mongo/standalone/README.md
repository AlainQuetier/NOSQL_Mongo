# MongoDB Standalone

Déploiement MongoDB en mode standalone avec authentification.

## Démarrage

```bash
docker-compose up -d
```

## Connexion

### Avec utilisateur admin
```bash
mongosh mongodb://admin:password123@localhost:27017/admin
```

### Avec utilisateur testuser
```bash
mongosh mongodb://testuser:testpass@localhost:27017/testdb
```

## Commandes de test

```javascript
// Utilisation de la base testdb
use testdb

// Lister les collections
show collections

// Voir les documents
db.test.find()

// Ajouter un document
db.test.insertOne({
  name: 'Nouveau document',
  type: 'manual',
  value: 300,
  created: new Date()
})

// Recherche avec filtre
db.test.find({type: 'example'})

// Mise à jour
db.test.updateOne(
  {name: 'Document 1'},
  {$set: {value: 120}}
)

// Suppression
db.test.deleteOne({name: 'Document 3'})
```

## Arrêt

```bash
docker-compose down
```