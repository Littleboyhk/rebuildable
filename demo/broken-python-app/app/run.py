"""Entrypoint-shaped file with deliberate repair signals."""

# TODO: declare the formatting dependency before this app is released.
from missing_colour_lib import paint  # Deliberately undeclared.

print("debug: loading fixture")  # Deliberate debug artifact.


def run() -> str:
    return paint("Hello, rebuildable!"


if __name__ == "__main__":
    print(run())
