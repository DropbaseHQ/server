import toml


def load_toml(file_name: str):
    with open(file_name) as file:
        return toml.load(file)


config = load_toml("config.toml")
worker_envs = load_toml("worker_envs.toml")
