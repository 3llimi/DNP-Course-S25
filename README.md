# DNP Course S25 Labs

Coursework for Distributed Systems and Network Programming (Spring 2025).

This repository contains three lab projects:
- Lab 1: UDP file transfer with Stop-and-Wait ARQ
- Lab 3: RabbitMQ message broker pipeline
- Lab 4: gRPC Connect Four server

## Repository Layout

```text
.
|-- lab1-3llimi/
|   |-- client/
|   |-- server/
|   `-- tests/
|-- lab3-3llimi/
|   |-- applications/
|   `-- tests/
`-- lab4-3llimi/
    |-- client.py
    |-- server.py
    |-- game.proto
    `-- tests/
```

## Prerequisites

- Python 3.10+ (3.11 recommended)
- Bash-compatible shell for running provided test scripts
- Docker (required for Lab 3 automated tests)

Optional tools used by tests:
- `autopep8` (Lab 1 formatting check)
- Linux `tc` traffic control command (Lab 1 packet-loss test)

## Quick Start

Clone and move into the repository root:

```bash
git clone https://github.com/3llimi/DNP-Course-S25.git
cd DNP-Course-S25
```

## Lab 1: Stop-and-Wait ARQ (UDP)

Location: `lab1-3llimi`

### Run manually

Start server:

```bash
cd lab1-3llimi
python3 server/server.py 8000
```

In another terminal, send a file with the provided client:

```bash
python3 client/client.py 127.0.0.1:8000 client/note.txt
```

### Run tests

From `lab1-3llimi`:

```bash
bash tests/1.sh
bash tests/2.sh
bash tests/3.sh
bash tests/4.sh
```

Notes:
- `tests/4.sh` requires Linux networking tools (`tc`) and suitable permissions.
- Tests expect `server/server.py` in place and validate transferred file integrity.

## Lab 3: RabbitMQ Message Pipeline

Location: `lab3-3llimi`

Applications in `applications/`:
- `Producer.py`
- `Squarer.py`
- `Cuber.py`
- `Logger.py`

### Install Python dependencies

```bash
cd lab3-3llimi
pip install -r requirements.txt
```

### Start test environment

The setup script launches RabbitMQ in Docker and writes test globals:

```bash
bash tests/setup.sh
```

### Run tests

```bash
bash tests/test0.sh
bash tests/test1.sh
bash tests/test2.sh
bash tests/test3.sh
```

Notes:
- The setup script creates a Docker network named `test` and runs `rabbitmq:4-alpine`.
- Tests start multiple Python processes and verify message/log behavior.

## Lab 4: gRPC Connect Four

Location: `lab4-3llimi`

### Install dependencies

```bash
cd lab4-3llimi
pip install grpcio grpcio-tools
```

### Compile proto

```bash
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. game.proto
```

### Run server and client

Start server:

```bash
python3 server.py 50051
```

Run clients (separate terminals):

```bash
python3 client.py localhost:50051 --automate --player R
python3 client.py localhost:50051 --automate --player Y --game_id 1
```

### Run tests

```bash
bash tests/1.sh
bash tests/2.sh
```

## Troubleshooting

- If `python3` is unavailable on Windows, replace with `python`.
- If Bash scripts do not run on Windows, use Git Bash, WSL, or run equivalent commands manually.
- For Lab 3, confirm Docker daemon is running before `tests/setup.sh`.

