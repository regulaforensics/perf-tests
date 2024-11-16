# Face API

For details, refer to the [Performance Guide](https://docs.regulaforensics.com/develop/face-sdk/web-service/administration/performance-guide/).

## Environment

### Start configuration

Env file: [./environment/.env](./environment/.env)

| Environment variable | Value                        | Info                               |
|----------------------|------------------------------|------------------------------------|
| IMAGE_TAG            | nightly-cpu                  | Docker image tag you want to start |
| REGULA_LICENSE_PATH  | ./environment/regula.license | Regula license file location       |
| CONFIG_FILE_PATH     | ./environment/config.yaml    | Face API config file location      |

### Face API service configuration

Face api service starts with settings specified in [config file ./environment/config.yaml](./environment/config.yaml)

### Prometheus configuration

Before starting, you need to set the URL where the locus tests will be launched [prometheus config file ./environment/prometheus/config.yml](./environment/prometheus/config.yml)

### Run services

```bash
docker compose --profile cpu|gpu --env-file ./environment/.env up -d
```

### Stop services

```bash
docker compose --env-file ./environment/.env down --remove-orphans
```

### Stop services and delete volumes
```bash
docker compose --env-file ./environment/.env down -v --remove-orphans
```

### Services

| Service     | Port         | Credentials                                                        |
|-------------|--------------|--------------------------------------------------------------------|
| FaceAPI     | 41101        |                                                                    |
| Postgres    | 5432         | User: regula <br> Password: Regulapasswd#1 <br> DB Name: regula_db |
| Minio       | 9000<br>9001 | User: minioadmin <br> Password: minioadmin                         |
| Grafana     | 9091         | User: admin <br> Password: admin                                   |
| Milvus attu | 3000         |                                                                    |



## Tests
It is better to run tests on different computers with face service.

### Local network test

Before starting the test, you need to determine the network bandwidth.

```bash
cd speed-test
docker build -t speed-test .
docker run --rm -e FACEAPI_HOST={FACEAPI_HOST}  speed-test
```
FACEAPI_HOST is the URL where the face service is raised.

### Start configuration

Env file: [./environment/.env](./environment/.env)

| Environment variable | Value                  | Info                                    |
|----------------------|------------------------|-----------------------------------------|
| FACEAPI_URL          | http://127.0.0.1:41101 | URL where face service is installed     |
| NUMBER_LOCUST_USERS  | 1                      | Peak number of concurrent Locust users. |
| SCENARIO             | UserLiveness           | Performance test run script             |

[All locust settings](https://docs.locust.io/en/stable/configuration.html)

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
