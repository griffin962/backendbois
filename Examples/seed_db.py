#!/usr/bin/env python3

from pathlib import Path

from natsort import natsorted

from sqlalchemy_seed import load_fixture_files, load_fixtures

import klap4.db
from klap4.db_entities import *


def main():
    script_dir = Path(__file__).absolute().parent.resolve(strict=True)
    data_dir = (script_dir/".."/"Dummy DB Data").resolve(strict=True)
    print(f"Searching for seed data in directory '{data_dir}' ...")

    klap4.db.connect(script_dir/".."/"test.db", reset=True)
    yaml_files = natsorted([path.name for path in data_dir.glob('*.yaml')])

    for yaml_file in yaml_files:
        print(f"Loading file: {yaml_file}")
        try:
            fixtures = load_fixture_files(data_dir, [yaml_file])
            load_fixtures(klap4.db.Session, fixtures)
        except Exception as e:
            raise RuntimeError(f"Error importing database data from file: {data_dir/yaml_file}") from e

    print("Done seeding data.")


if __name__ == '__main__':
    main()
