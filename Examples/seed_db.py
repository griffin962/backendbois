#!/usr/bin/env python3

from pathlib import Path

from natsort import natsorted

from sqlalchemy_seed import load_fixture_files, load_fixtures
import sqlalchemy

import klap4.db
import os
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

    # Open the .sql file
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    sql_load = os.path.join(THIS_FOLDER, 'program_slots.sql')
    sql_file = open(sql_load,'r')

    # Create an empty command string
    sql_command = ''

    session = klap4.db.Session()

    # Iterate over all lines in the sql file
    for line in sql_file:
        # Ignore commented lines
        if not line.startswith('--') and line.strip('\n'):
            # Append line to the command string
            sql_command += line.strip('\n')

            # If the command string ends with ';', it is a full statement
            if sql_command.endswith(';'):
                # Try to execute statement and commit it
                try:
                    session.execute(str(sql_command))
                    session.commit()

                # Finally, clear command string
                finally:
                    sql_command = ''

    print("Done seeding data.")


if __name__ == '__main__':
    main()
