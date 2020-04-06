#!/usr/bin/env python3

from pathlib import Path

from sqlalchemy_seed import load_fixture_files, load_fixtures

import klap4.db
from klap4.db_entities import *


def main():
    script_dir = Path(__file__).absolute().parent
    klap4.db.connect(script_dir/".."/"test.db", reset=True)
    yaml_files = [path.name for path in script_dir.glob('*.yaml')]
    print(f"Loaded files: {yaml_files}")
    fixtures = load_fixture_files(script_dir, yaml_files)
    load_fixtures(klap4.db.Session, fixtures)


if __name__ == '__main__':
    main()
