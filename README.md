# Mobile World — отказоустойчивый стенд MongoDB (проект 4 спринта)

Проектная работа курса «Архитектор ПО» Яндекс.Практикум. Исходный PoC интернет-магазина «Мобильный мир» был доработан: MongoDB шардирована на 2 шарда, каждый шард и config server развёрнуты как Replica Set из 3 узлов, перед базой добавлен Redis-кэш.

## Состав итогового стенда (sharding-repl-cache)

- `pymongo-api` — приложение (образ `kazhem/pymongo_api:1.0.0`), порт 8080.
- `redis` — кэш ответов для эндпоинта `/<collection>/users`.
- `mongos` — роутер шардированного кластера, порт 27020.
- `configSrv-1/2/3` — Replica Set конфигурационных серверов.
- `shard1-1/2/3` — Replica Set первого шарда.
- `shard2-1/2/3` — Replica Set второго шарда.

Схема итогового решения (а также все промежуточные варианты) — [diagrams/task1.drawio](diagrams/task1.drawio), 5 страниц: Sharding → Replication → Caching → Gateway & Consul → CDN.

## Как запустить

Требования: Docker с Docker Compose, минимум 2 CPU и 4 ГБ ОЗУ.

```bash
cd sharding-repl-cache
docker compose up -d
docker compose ps
```

Дождитесь, пока все контейнеры получат статус `Up` (обычно 10–20 секунд).

## Инициализация кластера

Все шаги автоматизированы в скрипте [scripts/init-sharding-repl-cache.sh](scripts/init-sharding-repl-cache.sh):

```bash
cd sharding-repl-cache
docker compose up -d
../scripts/init-sharding-repl-cache.sh
```

Если хочется выполнять команды вручную (или что-то пошло не так) — пошаговая инструкция с блоками `mongosh` лежит в [sharding-repl-cache/README.md](sharding-repl-cache/README.md). Скрипт делает ровно эти шаги:

1. `rs.initiate` на `configSrv-1` для Replica Set `config_replica_set`.
2. `rs.initiate` на `shard1-1` и `shard2-1` для Replica Set'ов шардов.
3. `sh.addShard` на `mongos` для обоих шардов.
4. `sh.enableSharding("somedb")` и `sh.shardCollection("somedb.helloDoc", { "name": "hashed" })`.
5. Вставка 1000 тестовых документов через `mongos`.

## Как проверить

- `http://localhost:8080/` — JSON с информацией о топологии (`mongo_topology_type: "Sharded"`), шардах и репликах, `cache_enabled: true`.
- `http://localhost:8080/docs` — Swagger API.
- `http://localhost:8080/somedb/users` — первый вызов ~1 сек, повторный < 100 мс (кэш Redis).
- Счётчик документов через `mongos`:
  ```bash
  docker compose exec -T mongos mongosh --port 27020 --quiet <<EOF
  use somedb;
  db.helloDoc.countDocuments();
  EOF
  ```

## Структура репозитория

- [mongo-sharding/](mongo-sharding/) — этап 1 (только шардирование, 2 шарда без реплик). Используется для сдачи задания 2.
- [mongo-sharding-repl/](mongo-sharding-repl/) — этап 2 (+ репликация, по 3 узла в каждой группе). Задание 3.
- [sharding-repl-cache/](sharding-repl-cache/) — **итоговая конфигурация** (+ Redis). Задание 4; именно её проверяет ревьюер.
- [diagrams/task1.drawio](diagrams/task1.drawio) — схемы для заданий 1, 5, 6.
- [docs/](docs/) — исходные описания заданий.
