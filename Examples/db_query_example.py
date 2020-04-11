#!/usr/bin/env python3

from pathlib import Path

from klap4 import db
from klap4.db_entities import *

from sqlalchemy.sql.expression import and_


def main():
    script_path = Path(__file__).absolute().parent
    db.connect(script_path/".."/"test.db")

    artist = get_entity_from_tag("AL1")

    print(get_json(artist))


if __name__ == '__main__':
    main()
