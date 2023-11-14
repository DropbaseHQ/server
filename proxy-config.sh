#!/bin/sh
cat << EOF > ./frpc.toml
# frpc.toml
serverAddr = "${DROPBASE_PROXY_SERVER_URL}"
serverPort = 7000

metadatas.token = "${DROPBASE_PROXY_SERVER_TOKEN}"

[[proxies]]
name = "${DROPBASE_PROXY_SERVER_TOKEN}/worker"
type = "tcp"
localIP = "127.0.0.1"
localPort = ${DROPBASE_WORKER_PORT:-9000}

[[proxies]]
name = "${DROPBASE_PROXY_SERVER_TOKEN}/lsp"
type = "tcp"
localIP = "127.0.0.1"
localPort = ${DROPBASE_LSP_PORT:-9001}
EOF
exec /usr/bin/frpc -c ./frpc.toml