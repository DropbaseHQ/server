import os
import platform
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path
import requests
from jinja2 import Environment, FileSystemLoader

DROPBASE_PROXY_SERVER_URL = os.getenv("DROPBASE_PROXY_SERVER_URL") or "proxy.app.dropbase.io"
DROPBASE_PROXY_SERVER_TOKEN = os.getenv("DROPBASE_PROXY_SERVER_TOKEN")
DROPBASE_WORKER_PORT = os.getenv("DROPBASE_WORKER_PORT") or 9000
DROPBASE_LSP_PORT = os.getenv("DROPBASE_LSP_PORT") or 9001

FRPC_DIR = Path(__file__).parent.absolute()
TEMPLATES_DIR = FRPC_DIR.joinpath("templates/")
FRPC_FILE = FRPC_DIR.joinpath("frpc")


if not os.path.isfile(FRPC_FILE):
    FRP_VERSION = "0.52.3"
    SYSTEM = platform.system().lower()
    MACHINE = platform.machine().lower()
    archive_name = f"frp_{FRP_VERSION}_{SYSTEM}_{MACHINE}"
    archive_ext = "zip" if SYSTEM == "windows" else "tar.gz"
    frp_url = (
        f"https://github.com/fatedier/frp/releases/download/v{FRP_VERSION}/{archive_name}.{archive_ext}"
    )
    r = requests.get(frp_url)
    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = Path(tmpdir).joinpath("frpzip")
        with open(archive_path, "wb") as wf:
            wf.write(r.content)

        if SYSTEM == "windows":
            import zipfile

            with zipfile.ZipFile(archive_path, "r") as rf:
                rf.extract(f"{archive_name}/frpc", tmpdir)
        else:
            import tarfile

            with tarfile.open(archive_path, "r:gz") as rf:
                rf.extract(f"{archive_name}/frpc", tmpdir)

        shutil.copyfile(f"{tmpdir}/{archive_name}/frpc", FRPC_FILE)
        os.chmod(FRPC_FILE, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


templates_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
frpc_config_template = templates_env.get_template("frpc.toml")

with tempfile.NamedTemporaryFile("w") as frpc_config_file:
    config_str = frpc_config_template.render(
        frpsServerAddr=DROPBASE_PROXY_SERVER_URL,
        frpsServerPort=7000,
        authToken=DROPBASE_PROXY_SERVER_TOKEN,
        workerProxyName=f"{DROPBASE_PROXY_SERVER_TOKEN}/worker",
        workerLocalPort=DROPBASE_WORKER_PORT,
        lspProxyName=f"{DROPBASE_PROXY_SERVER_TOKEN}/lsp",
        lspLocalPort=DROPBASE_LSP_PORT,
    )
    frpc_config_file.write(config_str)
    frpc_config_file.flush()
    subprocess.run([FRPC_FILE, "-c", frpc_config_file.name])

# FIXME token is logged in frpc output
