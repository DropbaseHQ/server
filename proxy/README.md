# Dropbase Worker Proxy Client

Use this script to securely expose your local worker and lsp deployments to Dropbase.

This proxy client is based on [frp](https://github.com/fatedier/frp) project.

### Setup

1. [Log in](https://app.dropbase.io/login) to your workspace and navigate to settings to generate a personal access token. Copy this token to your clipboard.
2. In your terminal navigate to the [dropbase repo](https://github.com/DropbaseHQ/dropbase) root.
3. Create `.env` and paste:
   ```
   DROPBASE_PROXY_SERVER_TOKEN=<PASTE YOUR TOKEN HERE>
   ```
4. Build the proxy docker image and run it using [Dockerfile-proxy](../Dockerfile-proxy)
