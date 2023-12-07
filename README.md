# Deploy server and lsp to docker

server

```
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
