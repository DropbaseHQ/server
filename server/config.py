import toml


def load_toml(file_name: str):
    with open(file_name) as file:
        return toml.load(file)


server_envs = load_toml("server.toml")
worker_envs = load_toml("worker.toml")
