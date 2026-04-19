#!/bin/bash

echo "Wait for databases to initialize their listeners..."
sleep 5

echo "Initializing config server..."
docker exec configSrv mongosh --port 27017 --eval "rs.initiate({_id: 'config_replica_set', configsvr: true, members: [{ _id : 0, host : 'configSrv:27017' }] })"
sleep 10

echo "Initializing shard 1..."
docker exec shard1 mongosh --port 27018 --eval "rs.initiate({_id: 'shard1', members: [{ _id : 0, host : 'shard1:27018' }] })"
sleep 10

echo "Initializing shard 2..."
docker exec shard2 mongosh --port 27019 --eval "rs.initiate({_id: 'shard2', members: [{ _id : 0, host : 'shard2:27019' }] })"
sleep 10

echo "Configuring router and sharding..."
docker exec mongos mongosh --port 27020 --eval "sh.addShard('shard1/shard1:27018'); sh.addShard('shard2/shard2:27019')"
sleep 5

echo "Enabling sharding for database 'somedb'..."
docker exec mongos mongosh --port 27020 --eval "sh.enableSharding('somedb'); sh.shardCollection('somedb.helloDoc', { 'name' : 'hashed' } );"
sleep 2

echo "Filling initial data..."
docker exec mongos mongosh --port 27020 --eval "db.getSiblingDB('somedb'); for(var i = 0; i < 1000; i++) db.getSiblingDB('somedb').helloDoc.insertOne({'age': i, 'name': 'user'+i});"

echo "Initialization complete!"
