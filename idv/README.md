# IDV Coordinator Performance Tests

## Environment

### Start configuration

Env file: [./environment/.env](./environment/.env)

Before starting services, place your `regula.license` file at `./environment/regula.license`.

| Environment variable | Value | Info |
|---|---|---|
| IDV_TAG | latest | IDV Coordinator image tag |
| FACEAPI_TAG | latest | Face API image tag |
| DOCREADER_TAG | latest | DocReader image tag |
| DOCKER_PLATFORM | linux/amd64 | Docker platform for IDV-related services |
| MONGODB_TAG | 8.0 | MongoDB image tag |
| OPENSEARCH_TAG | 3 | OpenSearch image tag |
| RABBITMQ_TAG | 3.13-management | RabbitMQ image tag |

### Run services

```bash
docker compose --env-file ./environment/.env up -d
```

### Stop services

```bash
docker compose --env-file ./environment/.env down --remove-orphans
```

### Stop services and delete volumes

```shell
docker compose --env-file ./environment/.env down -v --remove-orphans
```

### Services

| Service | Port | Credentials |
|---|---|---|
| IDV API | 8000 | User: regula-idv / Password: t3stP@ss |
| Face API | 41101 | - |
| DocReader | 8080 | - |
| MongoDB | 27017 | - |
| OpenSearch | 9200 | User: admin / Password: t3stP@ss!Pwd#2025 |
| RabbitMQ | 5672 / 15672 | User: admin / Password: admin |
| Prometheus | 9090 | - |
| Grafana | 9091 | User: admin / Password: admin |


## Tests

### Start configuration

Env file: [./locust-environment/.env](./locust-environment/.env)

| Environment variable | Value | Info |
|---|---|---|
| IDV_API_URL | http://webserver:8000 | URL where IDV service is running |
| NUMBER_LOCUST_USERS | 1 | Peak number of concurrent Locust users |
| SCENARIO | IDVViewGetByIdPerf | Performance test scenario |
| VIEW_NAMESPACE | active-views-3 | View namespace used for session discovery |

### Run tests

```shell
docker compose -f locust-docker-compose.yml --env-file ./locust-environment/.env up -d
```



`locust` starts the scenario automatically (`--autostart`) and exposes UI at `http://localhost:8089`.

To run with a different user count, edit `NUMBER_LOCUST_USERS` in `./locust-environment/.env` or override inline:

```shell
NUMBER_LOCUST_USERS=5 docker compose -f locust-docker-compose.yml --env-file ./locust-environment/.env up -d --force-recreate
```

```shell
NUMBER_LOCUST_USERS=10 docker compose -f locust-docker-compose.yml --env-file ./locust-environment/.env up -d --force-recreate
```

### Headless perf runs (5 minutes) with artifacts

Run `1` user for `5m`:

```shell
docker compose -f ./locust-docker-compose.yml --env-file ./locust-environment/.env run --rm --no-deps locust \
  -f /mnt/locust/locustfile.py IDVViewGetByIdPerf \
  -H http://webserver:8000 \
  --headless -u 1 -r 1 --run-time 5m \
  --csv=/mnt/locust/artifacts/u1/stats \
  --html=/mnt/locust/artifacts/u1/report.html
```

Run `5` users for `5m`:

```shell
docker compose -f ./locust-docker-compose.yml --env-file ./locust-environment/.env run --rm --no-deps locust \
  -f /mnt/locust/locustfile.py IDVViewGetByIdPerf \
  -H http://webserver:8000 \
  --headless -u 5 -r 1 --run-time 5m \
  --csv=/mnt/locust/artifacts/u5/stats \
  --html=/mnt/locust/artifacts/u5/report.html
```

Run `10` users for `5m`:

```shell
docker compose -f ./locust-docker-compose.yml --env-file ./locust-environment/.env run --rm --no-deps locust \
  -f /mnt/locust/locustfile.py IDVViewGetByIdPerf \
  -H http://webserver:8000 \
  --headless -u 10 -r 1 --run-time 5m \
  --csv=/mnt/locust/artifacts/u10/stats \
  --html=/mnt/locust/artifacts/u10/report.html
```

Artifacts will be stored in:

- `./locust-test/artifacts/u1`
- `./locust-test/artifacts/u5`
- `./locust-test/artifacts/u10`

### Stop tests

```shell
docker compose -f locust-docker-compose.yml --env-file ./locust-environment/.env down
```

### How metrics get to Grafana

1. `locust` generates load and runtime stats at `http://locust:8089`.
2. `locust-metrics-exporter` reads Locust stats and exposes Prometheus metrics at `:9646`.
3. Prometheus scrapes `locust-metrics-exporter:9646` (job `locust-monitoring`).
4. Grafana visualizes those Prometheus metrics at `http://localhost:9091`.

### Quick checks

```shell
docker compose -f locust-docker-compose.yml --env-file ./locust-environment/.env ps
```

```shell
docker compose -f locust-docker-compose.yml --env-file ./locust-environment/.env logs --tail=100 locust
```

```shell
curl -s http://localhost:9646/metrics | head
```

All statistics on the service and locust tests are available in Grafana at `http://localhost:9091` (`admin/admin`).

## Local Performance Testing

Run performance test locally without Docker:

```shell
cd locust-test && locust -f locustfile.py --host=http://localhost:8000
```

With parameters:

```shell
locust -f locustfile.py IDVViewGetByIdPerf --host=http://localhost:8000 -u 50 -r 10 --run-time 10m
```

### Available test scenario

- **IDVViewGetByIdPerf** (`view_search_and_get_by_id`) - calls `/api/views/namespaces/{namespace}`, builds a search body from view definition, runs `POST /api/sessions/search?limit=100`, and then loads each returned session via `/api/sessions/{session_id}`

### Nightly dataset precondition (100 sessions)

Before test run, export sessions from https://nightly-idv.regula.app/ and place archive (for example, `sessions-*.zip`) into `./environment/data/import`.
The DB is initialized from that archive by `setup` service (`idv session import -i /app/import`).
The scenario does not enforce an exact count in code and processes all sessions returned by `/api/sessions/search`.
If you need to reinitialize the environment from nightly archive, restart stack with volume cleanup:

```shell
docker compose --env-file ./environment/.env down -v --remove-orphans
docker compose --env-file ./environment/.env up -d
```

Web UI available at `http://localhost:8089`

## Monitoring Metrics

### Stack Overview

```
Locust Test (port 8089)
    ↓
Locust Metrics Exporter (port 9646)
    ↓
Prometheus (port 9090)
    ↓
Grafana (port 9091)
```

### Dashboards

Grafana dashboard "Locust Prometheus Monitoring Modern" shows:
- Requests Per Second (RPS)
- Response Time percentiles
- Total Requests
- Total Failures

Access at `http://localhost:9091` (admin/admin)

### Troubleshooting

If Grafana dashboard is empty:

1. Check if Locust is running and generating data:
   ```shell
   curl http://localhost:8089/stats/requests
   ```

2. Check if Metrics Exporter is connected:
   ```shell
   curl http://localhost:9646/metrics | head -20
   ```

3. Check Prometheus targets:
   ```shell
   curl http://localhost:9090/api/v1/targets
   ```

4. Check if data exists in Prometheus:
   ```shell
   curl 'http://localhost:9090/api/v1/query?query=locust_requests_current_rps'
   ```
