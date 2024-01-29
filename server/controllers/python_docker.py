import time

import docker

from server.constants import cwd


def run_container(env_vars: dict):
    client = docker.from_env()

    # specify the path to inside_docker.py on your host machine
    # make sure to provide the absolute path
    workspace_dir = cwd + "/workspace"
    # specify the mount point in the Docker container
    # container_path = '/app'
    # define the mount
    mount1 = docker.types.Mount(target="/app/workspace", source=workspace_dir, type="bind")
    # mount the dataframe.py file
    dataframe_file = cwd + "/worker"
    mount2 = docker.types.Mount(target="/app", source=dataframe_file, type="bind")

    # create inside_docker and mount to /app

    # Run the Docker container with the mount
    # container = client.containers.run('my-python-app', mounts=[mount], detach=True)
    container = client.containers.run(
        "worker",
        command="python inside_docker.py",
        mounts=[mount1, mount2],
        environment=env_vars,  # pass environment variables here
        detach=True,
        working_dir="/app",  # set working directory as /app
    )

    time.sleep(1)

    # Fetch and print container's log
    logs = container.logs()
    print(logs.decode("utf-8"))  # Decode bytes to string format.
    container.stop()

    container.stop()
