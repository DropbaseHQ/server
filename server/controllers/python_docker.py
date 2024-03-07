import json
import logging
import os

import docker
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def run_container(env_vars: dict, docker_script: str = "inside_docker"):

    client = docker.from_env()

    # add environment variables from .env file
    # TODO: revisit this, should only send .env variables to docker
    config = {key: os.getenv(key) for key in os.environ.keys()}
    env_vars = {**env_vars, **config}

    # get absolute path of the workspace directory from the environment variable
    host_path = os.getenv("HOST_WORKSPACE_PATH")
    workspace_mount = docker.types.Mount(
        target="/app/workspace", source=host_path + "/workspace", type="bind"
    )  # noqa
    files_mount = docker.types.Mount(target="/app/files", source=host_path + "/files", type="bind")
    mounts = [workspace_mount, files_mount]

    # add additional mounts from the environment variable
    if os.getenv("HOST_MOUNTS"):
        try:
            host_mounts = json.loads(os.getenv("HOST_MOUNTS")) or []
            for mount in host_mounts:
                mounts.append(
                    docker.types.Mount(
                        target=f"/app/{mount}", source=f"{host_path}/{mount}", type="bind"
                    )
                )
        except Exception as e:
            logger.warning(f"Error parsing HOST_MOUNTS: {e}")
            mounts = [workspace_mount, files_mount]

    # Run the Docker container with the mount
    client.containers.run(
        "dropbase/worker",
        command=f"python {docker_script}.py",
        mounts=mounts,
        environment=env_vars,
        network="dropbase_default",
        detach=True,
        working_dir="/app",
        auto_remove=True,
    )
