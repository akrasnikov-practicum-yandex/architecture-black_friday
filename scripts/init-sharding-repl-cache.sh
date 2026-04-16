#!/usr/bin/env bash
set -euo pipefail

# Инициализация итогового стенда sharding-repl-cache:
# - Replica Set конфигурационных серверов
# - Replica Set'ы для shard1 и shard2
# - Добавление шардов в mongos, включение шардирования
# - Наполнение коллекции somedb.helloDoc 1000 документами
#
# Запускать из директории sharding-repl-cache/, после `docker compose up -d`:
#   ../scripts/init-sharding-repl-cache.sh

run() {
  # $1 — имя сервиса, $2 — порт mongosh, $3 — блок команд
  docker compose exec -T "$1" mongosh --port "$2" --quiet <<EOF
$3
EOF
}

echo "==> 1/6 Инициализация Replica Set конфигурационных серверов"
run configSrv-1 27017 '
rs.initiate({
  _id: "config_replica_set",
  configsvr: true,
  members: [
    { _id: 0, host: "configSrv-1:27017" },
    { _id: 1, host: "configSrv-2:27017" },
    { _id: 2, host: "configSrv-3:27017" }
  ]
});
'

echo "==> 2/6 Инициализация Replica Set shard1"
run shard1-1 27018 '
rs.initiate({
  _id: "shard1",
  members: [
    { _id: 0, host: "shard1-1:27018" },
    { _id: 1, host: "shard1-2:27018" },
    { _id: 2, host: "shard1-3:27018" }
  ]
});
'

echo "==> 3/6 Инициализация Replica Set shard2"
run shard2-1 27019 '
rs.initiate({
  _id: "shard2",
  members: [
    { _id: 0, host: "shard2-1:27019" },
    { _id: 1, host: "shard2-2:27019" },
    { _id: 2, host: "shard2-3:27019" }
  ]
});
'

echo "==> Ожидание выборов Primary в Replica Set'ах (15 сек)"
sleep 15

echo "==> 4/6 Добавление шардов в mongos"
run mongos 27020 '
sh.addShard("shard1/shard1-1:27018,shard1-2:27018,shard1-3:27018");
sh.addShard("shard2/shard2-1:27019,shard2-2:27019,shard2-3:27019");
'

echo "==> 5/6 Включение шардирования для somedb.helloDoc"
run mongos 27020 '
sh.enableSharding("somedb");
sh.shardCollection("somedb.helloDoc", { "name": "hashed" });
'

echo "==> 6/6 Наполнение коллекции 1000 документами"
run mongos 27020 '
use somedb;
for (var i = 0; i < 1000; i++) db.helloDoc.insertOne({ age: i, name: "user" + i });
print("Total docs: " + db.helloDoc.countDocuments());
'

echo "==> Готово. Приложение: http://localhost:8080/"
