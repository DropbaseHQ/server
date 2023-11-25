# Deploy server and lsp to docker

server

```
docker build -t dropbase/server -f Dockerfile-server .
docker push dropbase/server
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
uvicorn server.main:app --reload --host 0.0.0.0 --port 9000
```

lsp

```
set -o allexport; source .env; set +o allexport
pylsp --ws --port 9001
```
