# Dropbase Worker Proxy Client

Use this script to securely expose your local worker and lsp deployments to Dropbase.

This proxy client is based on [frp](https://github.com/fatedier/frp) project.

### Setup

Before starting ensure that you are in a virtualenv and have installed requirements.txt from the repo root.

1. [Log in](https://app.dropbase.io/login) to your workspace and navigate to settings to generate a personal access token. Copy this token to your clipboard.
2. In your terminal navigate to the [worker repo](https://github.com/DropbaseHQ/dropbase) root.
3. Create `.env` and paste:
   ```
   DROPBASE_PROXY_SERVER_TOKEN=<PASTE YOUR TOKEN HERE>
   ```
4. Execute
   ```
   python proxy/main.py
   ```

To run this process in the background, try

```
nohup python worker-proxy-client/main.py &
```
