# Docreader

## Environment

### Start configuration

Env file: [./environment/.env](./environment/.env)

| Environment variable | Value                        | Info                               |
|----------------------|------------------------------|------------------------------------|
| IMAGE_TAG            | nightly                      | Docker image tag you want to start |
| REGULA_LICENSE_PATH  | ./environment/regula.license | Regula license file location       |
| CONFIG_FILE_PATH     | ./environment/config.yaml    | Docreader config file location     |

### Docreader service configuration

Docreader service starts with settings specified in [config file ./environment/config.yaml](./environment/config.yaml)

### Run services

```bash
docker compose --env-file ./environment/.env up -d
```

### Stop services

```bash
docker compose --env-file ./environment/.env down
```

### Stop services and delete volumes
```bash
docker compose --env-file ./environment/.env down -v
```

### Services

| Service     | Port         | Credentials                                                        |
|-------------|--------------|--------------------------------------------------------------------|
| Docreader   | 8080         |                                                                    |
| Postgres    | 5432         | User: regula <br> Password: Regulapasswd#1 <br> DB Name: regula_db |
| Minio       | 9000<br>9001 | User: minioadmin <br> Password: minioadmin                         |
| Grafana     | 9091         | User: admin <br> Password: admin                                   |



## Tests
It is better to run tests on different computers with docreader service

### Start configuration

Env file: [./environment/.env](./environment/.env)

| Environment variable | Value                 | Info                                     |
|----------------------|-----------------------|------------------------------------------|
| DOCREADERAPI_URL     | http://127.0.0.1:8080 | URL where docreader service is installed |
| NUMBER_LOCUST_USERS  | 1                     | Peak number of concurrent Locust users.  |
| SCENARIO             | UserApiV2             | Performance test run script              |

All [locust settings](https://docs.locust.io/en/stable/configuration.html)

### Run services

```bash
docker compose -f locust-docker-compose.yml --env-file ./environment/.env up -d
```

### Stop services

```bash
docker compose -f locust-docker-compose.yml --env-file ./environment/.env down
```

### Stop services and delete volumes
```bash
docker compose -f locust-docker-compose.yml --env-file ./environment/.env down -v
```

All statistics on the service and locust tests will be in Grafana
