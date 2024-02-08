# Deploy server and lsp to docker

server

```
docker buildx build --platform linux/amd64,linux/arm64 --push -t dropbase/server:0.0.7 -f Dockerfile-server .

docker build -t dropbase/server:0.0.2 -f Dockerfile-server .
docker push dropbase/server:0.0.2
```

latest

```
docker build -t dropbase/server:latest -f Dockerfile-server .
docker push dropbase/server:latest
```

lsp

```
docker buildx build --platform linux/amd64,linux/arm64 --push -t dropbase/lsp:0.0.4 -f Dockerfile-lsp .

docker build -t dropbase/lsp -f Dockerfile-lsp .
docker push dropbase/lsp
```

# local setup

server

```
set -o allexport; source .env; set +o allexport
uvicorn server.main:app --reload --host 0.0.0.0 --port 9090
```

lsp

```
set -o allexport; source .env; set +o allexport
pylsp --ws --port 9095
```

worker local

```
docker build -f Dockerfile-worker -t worker .
```

worker prod

```
cd worker
docker build -t worker .
```

## run tests

```
python3 -m pytest --cov=server --cov-config=server/.coveragerc  --cov-report=html server/tests -k test_create_table_req
```

test individual file

```
python3 -m pytest --cov=server --cov-config=server/.coveragerc --cov-report=html server/tests/worker/test_sync.py
```

add break point

```
import pdb; pdb.set_trace()
```
