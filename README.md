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

## Demo

Run the fixture walkthrough with either shell or Python:

```sh
bash demo/run_demo.sh
python demo/run_demo.py
```

The Python demo copies both projects to temporary directories, runs scan → fix
→ scan, and leaves the originals unchanged. The shell script delegates to the
same runner.

## Test

```sh
pytest
```
