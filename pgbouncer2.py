import re
from pathlib import Path

import docker

client = docker.from_env()

pgbouncer_config_dir = Path("/tmp/pgbouncer_config")
pgbouncer_config_file = pgbouncer_config_dir / "pgbouncer.ini"

pgbouncer_config_dir.mkdir(parents=True, exist_ok=True)

databases = [
    {"name": "db1", "user": "user1", "password": "password1"},
    {"name": "db2", "user": "user2", "password": "password2"},
]


def create_initial_config():
    pgbouncer_volume = {str(pgbouncer_config_dir): {"bind": "/etc/pgbouncer", "mode": "rw"}}

    container = client.containers.run(
        "edoburu/pgbouncer:latest",
        detach=True,
        volumes=pgbouncer_volume,
    )

    return container

    # Stop and remove the container (optional)
    # container.stop()
    # container.remove()


def update_pgbouncer_config(container, databases):
    volume_path = container.get_mounts()[0]["Source"]
    pgbouncer_config_file = Path(volume_path) / "pgbouncer.ini"

    with pgbouncer_config_file.open("r") as f:
        config_content = f.read()

    databases_start = config_content.find("[databases]\n")
    if databases_start == -1:
        databases_start = config_content.find("\n") + 1
        config_content = f"{config_content}\n[databases]\n"

    connection_string = "\n".join(
        [
            f'  {db["name"]} = host={db["host"]} port={db["port"]} dbname={db["name"]} user={db["user"]} password={db["password"]}\n'
            for db in databases
        ]
    )

    updated_config = (
        config_content[: databases_start + len("[databases]\n")]
        + connection_string
        + config_content[databases_start + len("[databases]\n") :]
    )

    with pgbouncer_config_file.open("w") as f:
        f.write(updated_config)


initial_config_container = create_initial_config()
update_pgbouncer_config(initial_config_container, databases)
