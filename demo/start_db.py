import os
import secrets
import subprocess
from pathlib import Path

import dotenv

# Setup .env
dotenv_path = dotenv.find_dotenv()

dotenv.set_key(dotenv_path, "SOURCE_PG_DROPBASEDEMODB_HOST", "host.docker.internal")
dotenv.set_key(dotenv_path, "SOURCE_PG_DROPBASEDEMODB_DATABASE", "dropbasedemodb")
dotenv.set_key(dotenv_path, "SOURCE_PG_DROPBASEDEMODB_USERNAME", "demouser")
dotenv.set_key(dotenv_path, "SOURCE_PG_DROPBASEDEMODB_PASSWORD", secrets.token_urlsafe(16))
dotenv.set_key(dotenv_path, "SOURCE_PG_DROPBASEDEMODB_PORT", "5432")

dotenv.load_dotenv(dotenv_path)


# Get path
DEMO_PATH = Path(__file__).parent.absolute()
DOCKERFILE_PATH = DEMO_PATH.joinpath("Dockerfile")


# Build and run Docker db
subprocess.run([
    "docker", "build",
    "-t", "dropbasedemodb",
    "-f", DOCKERFILE_PATH,
    "--build-arg", f"POSTGRES_DB={os.getenv('SOURCE_PG_DROPBASEDEMODB_DATABASE')}",
    "--build-arg", f"POSTGRES_USER={os.getenv('SOURCE_PG_DROPBASEDEMODB_USERNAME')}",
    "--build-arg", f"POSTGRES_PASSWORD={os.getenv('SOURCE_PG_DROPBASEDEMODB_PASSWORD')}",
    DEMO_PATH
]).check_returncode()
subprocess.run([
    "docker", "run",
    "-p", "5432:5432",
    "--network", "dropbase_default",
    "dropbasedemodb"
]).check_returncode()
