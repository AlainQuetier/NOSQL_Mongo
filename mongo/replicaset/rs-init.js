// Script d'initialisation du replica set
print('Initialisation du replica set rs0...');

// Configuration du replica set
rs.initiate({
  _id: "rs0",
  members: [
    {
      _id: 0,
      host: "mongo1:27017",
      priority: 2
    },
    {
      _id: 1,
      host: "mongo2:27017",
      priority: 1
    },
    {
      _id: 2,
      host: "mongo3:27017",
      priority: 1
    }
  ]
});

print('Replica set initialisé');
print('Attente de l\'élection du PRIMARY...');

// Attendre que le replica set soit prêt
sleep(5000);

// Vérifier le statut
print('Statut du replica set:');
rs.status();

// Création d'un utilisateur pour les tests
print('Création de l\'utilisateur testuser...');

// Changer vers la base testdb
use testdb;

// Créer un utilisateur pour testdb
db.createUser({
  user: 'testuser',
  pwd: 'testpass',
  roles: [
    {
      role: 'readWrite',
      db: 'testdb'
    }
  ]
});

// Insérer quelques documents de test
db.test.insertMany([
  {
    name: 'Document RS 1',
    type: 'replicaset',
    value: 1000,
    created: new Date()
  },
  {
    name: 'Document RS 2',
    type: 'replicaset',
    value: 2000,
    created: new Date()
  },
  {
    name: 'Document RS 3',
    type: 'replicaset',
    value: 1500,
    created: new Date()
  }
]);

print('Base de données testdb initialisée avec succès');
print('Utilisateur testuser créé');
print('Collection test créée avec 3 documents');
print('Replica set rs0 prêt!');