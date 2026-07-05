# Call-Analyzer

A small web application that lets users upload a short audio recording of a sales phone call (WAV or MP3), transcribe it with a speech-to-text (STT) model, and analyze the transcript with an LLM.

## Prerequisites

- [conda](https://docs.conda.io/) (for the Python environment)
- [yarn](https://yarnpkg.com/) (`brew install yarn`)
- Docker and Docker Compose (`brew install docker docker-compose`)

## Setup

### 1. Python environment

```sh
make create-environment
conda activate call-analyzer
make install-dependencies
```

### 2. Frontend dependencies

```sh
cd call_analyzer_web
yarn
cd ..
```

### 3. Environment variables

Create a `.env` file in the project root with:

```
POSTGRES_DATA_PATH={abspathtotheproject}/dbs/data
POSTGRES_DATA_BACKUPS_PATH={abspathtotheproject}/dbs/backups
```

To enable transcription, set `DEEPGRAM_API_KEY` in `call_analyzer_api/.envs/.local/.django` to a valid [Deepgram](https://deepgram.com/) API key. Without it, audio uploads will fail to transcribe.

## Running the app

```sh
make docker-compose-build
make up
```

Then navigate to [localhost:3000](http://localhost:3000).

A backend admin account is seeded for local development:

- email: `admin@test.com`
- password: `admin1234`

## Useful commands

| Command             | Description                                  |
| -------------------- | --------------------------------------------- |
| `make up`            | Start all containers                          |
| `make down`          | Stop all containers                           |
| `make restart`       | Restart all containers                        |
| `make rebuild`       | Rebuild images and restart containers         |
| `make logs`          | Tail the Django container logs                |
| `make attach`        | Attach to the running Django container        |
| `make test`          | Run the Django test suite                     |
| `make format`        | Format Django code with `black`               |
