#!/bin/sh
cat << EOF > ./frpc.toml
# frpc.toml
serverAddr = "${DROPBASE_PROXY_SERVER_URL}"
serverPort = 7000

metadatas.token = "${DROPBASE_PROXY_SERVER_TOKEN}"

[[proxies]]
name = "${DROPBASE_PROXY_SERVER_TOKEN}/worker"
type = "tcp"
localIP = "dropbase-server"
localPort = ${DROPBASE_WORKER_PORT:-9090}

[[proxies]]
name = "${DROPBASE_PROXY_SERVER_TOKEN}/lsp"
type = "tcp"
localIP = "dropbase-lsp"
localPort = ${DROPBASE_LSP_PORT:-9091}
EOF
exec /usr/bin/frpc -c ./frpc.toml