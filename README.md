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
