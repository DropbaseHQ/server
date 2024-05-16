import toml


def load_toml():
    with open("config.toml") as file:
        return toml.load(file)


config = load_toml()
