import os

import docker

from server.constants import cwd


def run_container(env_vars: dict, docker_script: str = "inside_docker"):

    client = docker.from_env()

    # add environment variables from .env file
    # TODO: revisit this, should only send .env variables to docker
    config = {key: os.getenv(key) for key in os.environ.keys()}
    env_vars = {**env_vars, **config}

    # mount workspace directory
    workspace_dir = cwd + "/workspace"
    mount1 = docker.types.Mount(target="/app/workspace", source=workspace_dir, type="bind")

    # Run the Docker container with the mount
    client.containers.run(
        "worker",
        command=f"python {docker_script}.py",
        mounts=[mount1],
        environment=env_vars,  # pass environment variables here
        detach=True,
        working_dir="/app",  # set working directory as /app
        auto_remove=True,
    )
