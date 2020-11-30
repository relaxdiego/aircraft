import os
from pathlib import Path
aircraft_dir = (Path(__file__) / '..').resolve()


def get_deployspec_path() -> Path:
    return os.environ['AIRCRAFT_DEPLOYSPEC']


def set_deployspec_path(path):
    os.environ['AIRCRAFT_DEPLOYSPEC'] = path
