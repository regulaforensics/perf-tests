# Face API

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
| FaceAPI     | 41101        |                                                                    |
| Postgres    | 5432         | User: regula <br> Password: Regulapasswd#1 <br> DB Name: regula_db |
| Minio       | 9000<br>9001 | User: minioadmin <br> Password: minioadmin                         |
| Grafana     | 9091         | User: admin <br> Password: admin                                   |
| Milvus attu | 3000         |                                                                    |



## Tests
TBD