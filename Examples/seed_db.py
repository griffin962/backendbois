#!/usr/bin/env python3

from pathlib import Path

from sqlalchemy_seed import load_fixture_files, load_fixtures

import klap4.db
from klap4.db_entities import *


def main():
    script_dir = Path(__file__).absolute().parent
    data_dir = script_dir/".."/"Dummy DB Data"
    print(f"Searching for seed data in directory '{data_dir}' ...")

    klap4.db.connect(script_dir/".."/"test.db", reset=True)
    yaml_files = sorted([path.name for path in data_dir.glob('*.yaml')])

    for yaml_file in yaml_files:
        print(f"Loading file: {yaml_file}")
        fixtures = load_fixture_files(data_dir, [yaml_file])
        load_fixtures(klap4.db.Session, fixtures)

    print("Done seeding data.")


if __name__ == '__main__':
    main()
