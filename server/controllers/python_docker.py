import json
import logging

import docker
from docker.errors import ContainerError

from server.config import worker_envs
from server.constants import AUTO_REMOVE_CONTAINER, HOST_MOUNTS, HOST_PATH

logger = logging.getLogger(__name__)


def stringify_env_vars(env_vars: dict) -> dict:
    stringified_env_vars = {}
    for key, value in env_vars.items():
        if isinstance(value, dict) or isinstance(value, list):
            stringified_env_vars[key] = json.dumps(value)
        else:
            stringified_env_vars[key] = value
    return stringified_env_vars


def run_container(env_vars: dict, docker_script: str = "inside_docker"):
    client = docker.from_env()

    # add environment variables from .worker_envs
    worker_envs_str = stringify_env_vars(worker_envs)
    env_vars = {**env_vars, **worker_envs_str}

    # get absolute path of the workspace directory from the environment variable
    workspace_mount = docker.types.Mount(
        target="/app/workspace", source=HOST_PATH + "/workspace", type="bind"
    )
    files_mount = docker.types.Mount(target="/app/files", source=HOST_PATH + "/files", type="bind")
    mounts = [workspace_mount, files_mount]

    # add additional mounts from the environment variable
    for mount in HOST_MOUNTS:
        # NOTE: we need to get the last part of the path to use as the target since all
        # directories are mounted to /app
        dir_name = mount.split("/")[-1]
        target = f"/app/{dir_name}"
        source = f"{mount}"
        mounts.append(docker.types.Mount(target=target, source=source, type="bind"))

    # Run the Docker container with the mount
    try:
        client.containers.run(
            "dropbase/worker",
            command=f"python {docker_script}.py",
            mounts=mounts,
            environment=env_vars,
            network="dropbase_default",
            working_dir="/app",
            detach=True,
            auto_remove=AUTO_REMOVE_CONTAINER,
        )
    except ContainerError as e:
        raise e
