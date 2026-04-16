# MongoDB Sharding + Replication + Redis Caching (Task 4)

Этот проект содержит `compose.yaml`, в котором настроен третий, наиболее полный вариант архитектурной схемы:
- **Шардирование базы данных** MongoDB.
- **Репликация (отказоустойчивость)**: каждый компонент инфраструктуры данных состоит из **Replica Set** по 3 узла.
- **Кеширование**: добавлен инстанс Redis для ускорения ответов приложения и снятия нагрузки с БД.

Каждый элемент данных состоит из Replica Set:
- Config Server (`configSrv-1`, `configSrv-2`, `configSrv-3`)
- Shard 1 (`shard1-1`, `shard1-2`, `shard1-3`)
- Shard 2 (`shard2-1`, `shard2-2`, `shard2-3`)

## Быстрый запуск (рекомендуется)

Все шаги ниже автоматизированы в скрипте [../scripts/init-sharding-repl-cache.sh](../scripts/init-sharding-repl-cache.sh):

```bash
docker compose up -d
../scripts/init-sharding-repl-cache.sh
```

После этого можно сразу открывать `http://localhost:8080/` — см. раздел «Проверка работы приложения и кеширования» ниже.

## Как запустить кластер (по шагам вручную)

1. **Запустите контейнеры:**
В терминале, из локальной папки `sharding-repl-cache`, выполните:
```bash
docker compose up -d
```
Подождите несколько секунд и проверьте, что все контейнеры (включая `redis` и `pymongo_api`) запущены.

2. **Инициализируйте конфигурационный сервер (Replica Set из 3 узлов):**
```bash
docker compose exec -T configSrv-1 mongosh --port 27017 --quiet <<EOF
rs.initiate(
  {
    _id: "config_replica_set",
    configsvr: true,
    members: [
      { _id : 0, host : "configSrv-1:27017" },
      { _id : 1, host : "configSrv-2:27017" },
      { _id : 2, host : "configSrv-3:27017" }
    ]
  }
);
EOF
```

3. **Инициализируйте шарды (Replica Sets из 3 узлов каждый):**

Для **shard1**:
```bash
docker compose exec -T shard1-1 mongosh --port 27018 --quiet <<EOF
rs.initiate(
  {
    _id: "shard1",
    members: [
      { _id : 0, host : "shard1-1:27018" },
      { _id : 1, host : "shard1-2:27018" },
      { _id : 2, host : "shard1-3:27018" }
    ]
  }
);
EOF
```

Для **shard2**:
```bash
docker compose exec -T shard2-1 mongosh --port 27019 --quiet <<EOF
rs.initiate(
  {
    _id: "shard2",
    members: [
      { _id : 0, host : "shard2-1:27019" },
      { _id : 1, host : "shard2-2:27019" },
      { _id : 2, host : "shard2-3:27019" }
    ]
  }
);
EOF
```

4. **Добавьте шарды в роутер (mongos):**
Мы указываем роутеру имена replica set'ов вместе с их хостами.
```bash
docker compose exec -T mongos mongosh --port 27020 --quiet <<EOF
sh.addShard("shard1/shard1-1:27018,shard1-2:27018,shard1-3:27018");
sh.addShard("shard2/shard2-1:27019,shard2-2:27019,shard2-3:27019");
EOF
```

5. **Включите шардирование базы данных и коллекции:**
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

## Проверка работы приложения и кеширования

Откройте в браузере (или выполните GET-запрос):
`http://localhost:8080/somedb/users`

**Как проверить работу Redis-кеша:**
1. При первом обращении на этот эндпоинт загрузка займёт больше секунды (в приложении намеренно установлен `time.sleep(1)` для имитации долгой работы).
2. Обновите страницу (сделайте второй вызов того же эндпоинта). Из-за включённого Redis этот запрос отработает мгновенно (**<100мс**), так как ответ будет отдан из кеша, минуя обращение к MongoDB.

Вы также можете проверить корневой эндпоинт `http://localhost:8080/`, чтобы увидеть `cache_enabled: true`, а также получить полный отчёт о текущих шардах и репликах.
