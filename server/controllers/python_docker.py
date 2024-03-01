import os

import docker
from dotenv import load_dotenv

load_dotenv()


def run_container(env_vars: dict, docker_script: str = "inside_docker"):

    client = docker.from_env()

    # add environment variables from .env file
    # TODO: revisit this, should only send .env variables to docker
    config = {key: os.getenv(key) for key in os.environ.keys()}
    env_vars = {**env_vars, **config}

    # replace localhost with host.docker.internal
    for key, value in env_vars.items():
        if value == "localhost":
            env_vars[key] = "host.docker.internal"

    # get absolute path of the workspace directory from the environment variable
    workspace_dir = os.getenv("HOST_WORKSPACE_PATH") + "/workspace"
    mount1 = docker.types.Mount(target="/app/workspace", source=workspace_dir, type="bind")

    # Run the Docker container with the mount
    client.containers.run(
        "dropbase/worker",
        command=f"python {docker_script}.py",
        mounts=[mount1],
        environment=env_vars,
        network="dropbase_default",
        detach=True,
        working_dir="/app",
        auto_remove=True,
    )
