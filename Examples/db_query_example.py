#!/usr/bin/env python3

from pathlib import Path

from klap4 import db
from klap4.db_entities import *

from sqlalchemy.sql.expression import and_


def main():
    script_path = Path(__file__).absolute().parent
    db.connect(script_path/".."/"test.db")

    session = db.Session()

    artist = session.query(Artist) \
        .filter(
            and_(
                Artist.genre_abbr == "AL",
                Artist.number == 2
            )
        ) \
        .first()

    print(artist)


if __name__ == '__main__':
    main()
