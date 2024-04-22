from pathlib import Path

import docker

postgres_host = "your_postgres_host"
postgres_port = 5432

databases = [
    {"name": "db1", "user": "user1", "password": "password1"},
    {"name": "db2", "user": "user2", "password": "password2"},
]

pgbouncer_config_dir = Path("/tmp/pgbouncer_config")
pgbouncer_config_file = pgbouncer_config_dir / "pgbouncer.ini"

# Ensure the directory exists
pgbouncer_config_dir.mkdir(parents=True, exist_ok=True)

# Generate PgBouncer configuration content
pgbouncer_config = "[databases]\n"
for db in databases:
    pgbouncer_config += f'  {db["name"]} = host={postgres_host} port={postgres_port} dbname={db["name"]} user={db["user"]} password={db["password"]}\n'

pgbouncer_config += """
[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = md5
# ... other PgBouncer configuration options ...
"""

with pgbouncer_config_file.open("w") as f:
    f.write(pgbouncer_config)

client = docker.from_env()

# Define the Docker volume mapping
pgbouncer_volume = {str(pgbouncer_config_dir): {"bind": "/etc/pgbouncer", "mode": "rw"}}

# Run the PgBouncer container with the volume
container = client.containers.run(
    "edoburu/pgbouncer:latest",
    detach=True,
    environment={
        "DB_HOST": postgres_host,
        "DB_PORT": str(postgres_port),
    },
    volumes=pgbouncer_volume,
    ports={"6432/tcp": "6432/tcp"},
)

print(f"PgBouncer container ID: {container.id}")

import psycopg2

connection_params = {
    "dbname": "db1",
    "user": "user1",
    "password": "password1",
    "host": "localhost",
    "port": 6432,
}

conn_string = " ".join([f"{k}={v}" for k, v in connection_params.items()])
conn = psycopg2.connect(conn_string)

cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())

conn.close()

# Stop and remove the container (optional)
# container.stop()
# container.remove()
