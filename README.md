# rebuildable

Offline Python 3.12 CLI that checks whether a project can be rebuilt on a clean Linux machine.

## Setup

```sh
python -m pip install -r requirements.txt -r requirements-dev.txt
```

## Run

```sh
python -m rebuildable scan .
python -m rebuildable fix . --dry-run
python -m rebuildable verify .
```

## Test

```sh
pytest
```
