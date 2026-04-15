# MongoDB Sharding (Task 2)

Этот проект содержит `compose.yaml`, в котором настроен первый вариант архитектурной схемы — базовое шардирование базы данных MongoDB.

## Как запустить кластер

1. **Запустите контейнеры:**
В терминале (находясь в папке `mongo-sharding`) выполните:
```bash
docker compose up -d
```
Подождите несколько секунд, чтобы базы запустились. Убедитесь, что все статусы — `Up`:
```bash
docker compose ps
```

2. **Инициализируйте конфигурационный сервер:**
```bash
docker compose exec -T configSrv mongosh --port 27017 --quiet <<EOF
rs.initiate(
  {
    _id: "config_replica_set",
    configsvr: true,
    members: [
      { _id : 0, host : "configSrv:27017" }
    ]
  }
);
EOF
```

3. **Инициализируйте шарды:**
Для первого шарда:
```bash
docker compose exec -T shard1 mongosh --port 27018 --quiet <<EOF
rs.initiate(
  {
    _id: "shard1",
    members: [
      { _id : 0, host : "shard1:27018" }
    ]
  }
);
EOF
```

Для второго шарда:
```bash
docker compose exec -T shard2 mongosh --port 27019 --quiet <<EOF
rs.initiate(
  {
    _id: "shard2",
    members: [
      { _id : 0, host : "shard2:27019" }
    ]
  }
);
EOF
```

4. **Добавьте шарды в роутер (mongos):**
```bash
docker compose exec -T mongos mongosh --port 27020 --quiet <<EOF
sh.addShard("shard1/shard1:27018");
sh.addShard("shard2/shard2:27019");
EOF
```

5. **Включите шардирование базы данных и коллекции:**
Мы будем использовать базу `somedb` и коллекцию `helloDoc` с шардированием по хешу от поля `name`.
```bash
docker compose exec -T mongos mongosh --port 27020 --quiet <<EOF
sh.enableSharding("somedb");
sh.shardCollection("somedb.helloDoc", { "name" : "hashed" } );
EOF
```

6. **Создайте тестовые данные:**
Наполним коллекцию 1000 документами, чтобы проверить распределение. Запрос отправляется на роутер `mongos`.
```bash
docker compose exec -T mongos mongosh --port 27020 --quiet <<EOF
use somedb;
for(var i = 0; i < 1000; i++) db.helloDoc.insertOne({"age": i, "name": "user"+i});
EOF
```

7. **Проверьте распределение документов:**

Узнать общее количество на роутере:
```bash
docker compose exec -T mongos mongosh --port 27020 --quiet <<EOF
use somedb;
db.helloDoc.countDocuments();
EOF
```

Посмотреть количество документов на **shard1**:
```bash
docker compose exec -T shard1 mongosh --port 27018 --quiet <<EOF
use somedb;
db.helloDoc.countDocuments();
EOF
```

Посмотреть количество документов на **shard2**:
```bash
docker compose exec -T shard2 mongosh --port 27019 --quiet <<EOF
use somedb;
db.helloDoc.countDocuments();
EOF
```

### Проверка в приложении
Вы также можете посмотреть статус работы кластера, открыв `http://localhost:8080/` (или `http://127.0.0.1:8080/docs` для Swagger). Данный эндпоинт вернёт конфигурацию системы, включая список шардов.
