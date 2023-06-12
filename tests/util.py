import json
import os
import sys
import pathlib
from typing import TypeAlias

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


def get_test_file(name: str) -> pathlib.Path:
    basedir = os.path.dirname(__file__)
    return pathlib.Path(basedir, "mocked_data", name)


def load_json(filename: pathlib.Path) -> JSON:
    with open(filename) as data:
        return json.load(data)
