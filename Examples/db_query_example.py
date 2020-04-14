#!/usr/bin/env python3

from pathlib import Path

from klap4 import db
from klap4.db_entities import *


def main():
    script_path = Path(__file__).absolute().parent
    db.connect(script_path/".."/"test.db")
    session = db.Session()

    artist = get_entity_from_tag("AL1")

    print(get_json(artist))
    print(artist.genre.name)
    print(type(artist))

    artist_list = search_artists("Al", "K")
    print(artist_list)

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    max_num = Artist(genre_abbr="AL", name="Test")

    session.add(max_num)
    session.commit()

    print(max_num)


if __name__ == '__main__':
    main()
