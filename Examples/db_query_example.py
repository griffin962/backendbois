#!/usr/bin/env python3

from pathlib import Path

from klap4 import db
from klap4.db_entities import *
from klap4.utils import *


def playlist_demo():
    print("PLAYLIST DEMO")
    playlist = get_entity_from_tag("jam4x2+My Playlist")

    for entry in playlist.entries:

        print(entry)
        print(entry.get_song_data())

    print("\n\n")


def simple_tag_fetch_demo():
    print("TAG FETCH DEMO")
    artist = get_entity_from_tag("AL1")

    print(get_json(artist))
    print(artist.genre.name)

    print("\n\n")


def main():
    script_path = Path(__file__).absolute().parent
    db.connect(script_path/".."/"test.db")

    simple_tag_fetch_demo()
    playlist_demo()


if __name__ == '__main__':
    main()
