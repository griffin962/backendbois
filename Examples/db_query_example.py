#!/usr/bin/env python3

from pathlib import Path

from klap4 import db
from klap4.db_entities import *
from klap4.utils import *
from klap4.services.album_services import generate_chart, charts_format, display_album
from klap4.services.program_services import get_program_slots


def playlist_demo():
    print("PLAYLIST DEMO")
    playlist = get_entity_from_tag("jam4x2+My Playlist")

    for entry in playlist.entries:

        print(entry)
        print(entry.get_song_data())

    print("\n\n")


def simple_tag_fetch_demo():
    print("TAG FETCH DEMO")
    album = get_entity_from_tag("RK3A")

    print(get_json(album))
    print(album.id)

    print("\n\n")


def charts_test():
    print("CHARTS DEMO")
    from datetime import datetime, timedelta

    thing = generate_chart("all")
    print(thing)
    thing2 = charts_format(thing)
    print(thing2)

    print("\n\n")


def main():
    script_path = Path(__file__).absolute().parent
    db.connect(script_path/".."/"test.db")

    s = get_program_slots()
    print(s)
    q = get_entity_from_tag('EXQ1')

if __name__ == '__main__':
    main()
