# import time

import docker

from server.constants import cwd


def run_container(env_vars: dict, docker_script: str = "inside_docker"):
    client = docker.from_env()

    # mount workspace directory
    workspace_dir = cwd + "/workspace"
    mount1 = docker.types.Mount(target="/app/workspace", source=workspace_dir, type="bind")
    # mount worker files
    worker_files = cwd + "/worker"
    mount2 = docker.types.Mount(target="/app", source=worker_files, type="bind")

    # Run the Docker container with the mount
    container = client.containers.run(
        "worker",
        command=f"python {docker_script}.py",
        mounts=[mount1, mount2],
        environment=env_vars,  # pass environment variables here
        detach=True,
        working_dir="/app",  # set working directory as /app
    )

    # time.sleep(1)
    # # Fetch and print container's log
    # logs = container.logs()
    # print(logs.decode("utf-8"))  # Decode bytes to string format.

    container.stop()
