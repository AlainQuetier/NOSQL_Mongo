// Script d'initialisation MongoDB
print('Initialisation de la base de données testdb...');

// Connexion à la base testdb
db = db.getSiblingDB('testdb');

// Création d'un utilisateur pour testdb
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

// Création d'une collection test avec quelques documents
db.test.insertMany([
  {
    name: 'Document 1',
    type: 'example',
    value: 100,
    created: new Date()
  },
  {
    name: 'Document 2',
    type: 'sample',
    value: 200,
    created: new Date()
  },
  {
    name: 'Document 3',
    type: 'example',
    value: 150,
    created: new Date()
  }
]);

print('Base de données testdb initialisée avec succès');
print('Utilisateur testuser créé');
print('Collection test créée avec 3 documents');