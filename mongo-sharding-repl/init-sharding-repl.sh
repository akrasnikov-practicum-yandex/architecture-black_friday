#!/bin/bash

echo "Wait for databases to initialize their listeners..."
sleep 15

echo "Initializing config server replica set..."
docker exec configSrv-1 mongosh --port 27017 --eval "rs.initiate({_id: 'config_replica_set', configsvr: true, members: [{ _id : 0, host : 'configSrv-1:27017' }, { _id : 1, host : 'configSrv-2:27017' }, { _id : 2, host : 'configSrv-3:27017' }] })"
sleep 10

echo "Initializing shard 1 replica set..."
docker exec shard1-1 mongosh --port 27018 --eval "rs.initiate({_id: 'shard1', members: [{ _id : 0, host : 'shard1-1:27018' }, { _id : 1, host : 'shard1-2:27018' }, { _id : 2, host : 'shard1-3:27018' }] })"
sleep 10

echo "Initializing shard 2 replica set..."
docker exec shard2-1 mongosh --port 27019 --eval "rs.initiate({_id: 'shard2', members: [{ _id : 0, host : 'shard2-1:27019' }, { _id : 1, host : 'shard2-2:27019' }, { _id : 2, host : 'shard2-3:27019' }] })"
sleep 10

echo "Configuring router and sharding..."
docker exec mongos mongosh --port 27020 --eval "sh.addShard('shard1/shard1-1:27018,shard1-2:27018,shard1-3:27018'); sh.addShard('shard2/shard2-1:27019,shard2-2:27019,shard2-3:27019')"
sleep 5

echo "Enabling sharding for database 'somedb'..."
docker exec mongos mongosh --port 27020 --eval "sh.enableSharding('somedb'); sh.shardCollection('somedb.helloDoc', { 'name' : 'hashed' } );"
sleep 2

echo "Filling initial data..."
docker exec mongos mongosh --port 27020 --eval "for(var i = 0; i < 1000; i++) db.getSiblingDB('somedb').helloDoc.insertOne({'age': i, 'name': 'user'+i});"

echo "Initialization complete!"
