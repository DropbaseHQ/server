# Dropbase Server

This repository contains the server codebase for [Dropbase](https://github.com/DropbaseHQ/dropbase). It contains the following services:

- `Server` - processes client requests and spins up a task worker to run Dropbase Functions. The server also updates page properties via context.
- `LSP Server` - enables auto-complete and auto-saving of Python code in Studio
- `Worker` - runs Dropbase Functions with the user inputs passed through via the client. It’s built as an async task runner.
- `Dropbase Package` - contains system-wide schemas, models and utility functions

## Prerequisites

- Python > 3.11
- [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)
- [Docker](https://docs.docker.com/engine/install/)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Create Virtual Environment

Create a virtual environment for the project:

```sh
python3 -m venv .venv
```

Activate the virtual environment:

```sh
source .venv/bin/activate
```

NOTE: Use the same `.venv` virtual environment to run the server, worker, and LSP.

### Install Dependencies

Install the project dependencies:

```sh
pip install -r requirements.txt
pip install -r requirements-worker.txt
pip install -r requirements-lsp.txt
```

### Make run.sh Executable

Make the `run.sh` script executable:

```sh
chmod +x run.sh
```

### Run the Server

Run the server:

```sh
./run.sh s
```

### Run the LSP Server

In a separate terminal, run the LSP server:

```sh
./run.sh l
```

### Run the Redis Server

In a separate terminal, run the Redis server:

```sh
redis-server
```

## Contributing

We welcome contributions to improve Dropbase. To contribute, please fork the repository, create a branch for your feature or bug fix, and submit a pull request.

1. Create a feature branch
2. Commit your changes
3. Push to the branch
4. Open a pull request

If you plan to make significant changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the DROPBASE SOFTWARE LICENSE (DSL) - see the [LICENSE.md](LICENSE.md) file for details. At the high level, the DSL grants you the right to use and modify the software for free as long as it's for non-commercial use.
