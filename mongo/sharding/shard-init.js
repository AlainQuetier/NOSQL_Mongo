// Script d'initialisation du sharding MongoDB
print('=== Initialisation du sharding MongoDB ===');

// Fonction helper pour attendre
function waitForConnection(host, maxRetries = 10) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            let conn = new Mongo(host);
            conn.getDB('admin').runCommand({ping: 1});
            print(`Connexion réussie à ${host}`);
            return conn;
        } catch (e) {
            print(`Tentative ${i + 1}/${maxRetries} pour ${host}...`);
            sleep(3000);
        }
    }
    throw new Error(`Impossible de se connecter à ${host}`);
}

// 1. Initialiser les replica sets des config servers
print('\n1. Initialisation du replica set des config servers...');
try {
    let configConn = waitForConnection('configsvr1:27017');
    configConn.getDB('admin').runCommand({
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
    print('Replica set des config servers initialisé');
} catch (e) {
    print(`Erreur config servers: ${e}`);
}

// Attendre que les config servers soient prêts
sleep(10000);

// 2. Initialiser les replica sets des shards
print('\n2. Initialisation des replica sets des shards...');

// Shard 1
try {
    let shard1Conn = waitForConnection('shard1:27017');
    shard1Conn.getDB('admin').runCommand({
        replSetInitiate: {
            _id: 'shard1ReplSet',
            members: [
                {_id: 0, host: 'shard1:27017'}
            ]
        }
    });
    print('Shard 1 replica set initialisé');
} catch (e) {
    print(`Erreur shard 1: ${e}`);
}

// Shard 2
try {
    let shard2Conn = waitForConnection('shard2:27017');
    shard2Conn.getDB('admin').runCommand({
        replSetInitiate: {
            _id: 'shard2ReplSet',
            members: [
                {_id: 0, host: 'shard2:27017'}
            ]
        }
    });
    print('Shard 2 replica set initialisé');
} catch (e) {
    print(`Erreur shard 2: ${e}`);
}

// Shard 3
try {
    let shard3Conn = waitForConnection('shard3:27017');
    shard3Conn.getDB('admin').runCommand({
        replSetInitiate: {
            _id: 'shard3ReplSet',
            members: [
                {_id: 0, host: 'shard3:27017'}
            ]
        }
    });
    print('Shard 3 replica set initialisé');
} catch (e) {
    print(`Erreur shard 3: ${e}`);
}

// Attendre que les shards soient prêts
sleep(15000);

// 3. Se connecter au mongos et configurer le sharding
print('\n3. Configuration du sharding via mongos...');

try {
    // Créer un utilisateur admin sur le mongos
    print('Création de l\'utilisateur admin...');
    db.getSiblingDB('admin').createUser({
        user: 'admin',
        pwd: 'password123',
        roles: ['root']
    });
    print('Utilisateur admin créé');

    // Ajouter les shards
    print('Ajout des shards...');
    sh.addShard('shard1ReplSet/shard1:27017');
    sh.addShard('shard2ReplSet/shard2:27017');
    sh.addShard('shard3ReplSet/shard3:27017');
    print('Shards ajoutés');

    // Activer le sharding pour la base sharddb
    print('Activation du sharding pour sharddb...');
    sh.enableSharding('sharddb');
    print('Sharding activé pour sharddb');

    // Créer un utilisateur pour sharddb
    print('Création de l\'utilisateur testuser...');
    db.getSiblingDB('sharddb').createUser({
        user: 'testuser',
        pwd: 'testpass',
        roles: [
            {
                role: 'readWrite',
                db: 'sharddb'
            }
        ]
    });
    print('Utilisateur testuser créé');

    // Créer et sharder la collection products
    print('Configuration du sharding pour la collection products...');
    sh.shardCollection('sharddb.products', {category: 1, _id: 1});
    print('Collection products shardée sur {category: 1, _id: 1}');

    // Insérer des données de test
    print('Insertion de données de test...');
    use sharddb;
    
    const categories = ['electronics', 'clothing', 'books', 'sports', 'home'];
    const products = [];
    
    for (let i = 0; i < 1000; i++) {
        products.push({
            _id: i,
            name: `Product ${i}`,
            category: categories[i % 5],
            price: Math.floor(Math.random() * 1000) + 1,
            stock: Math.floor(Math.random() * 100) + 1,
            created: new Date()
        });
    }
    
    db.products.insertMany(products);
    print('1000 produits de test insérés');

    // Afficher le statut du sharding
    print('\n4. Statut du sharding:');
    sh.status();
    
    print('\n=== Sharding MongoDB initialisé avec succès! ===');
    
} catch (e) {
    print(`Erreur lors de la configuration du sharding: ${e}`);
}
