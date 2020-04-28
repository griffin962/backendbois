#!/usr/bin/env python3

from datetime import datetime, timedelta

from sqlalchemy import Column, ForeignKey, Boolean, DateTime, String, Integer
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import and_

import klap4.db
from klap4.db_entities.artist import Artist
from klap4.db_entities.album import Album, find_artist_id
from klap4.db_entities import decompose_tag, SQLBase


def find_album_id(genre_abbr: str, artist_num: int, album_letter: str):
    entity = None

    try:
        from klap4.db import Session
        session = Session()

        artist_id = find_artist_id(genre_abbr, artist_num)
        entity = session.query(Album) \
            .filter(Album.artist_id == artist_id, Album.letter == album_letter).one()
        
        return entity.id
    except:
        raise "error"



class Song(SQLBase):
    __tablename__ = "song"

    class FCC_STATUS:
        CLEAN = 1
        INDECENT = 2
        OBSCENE = 3
        UNRATED = 4

    id = Column(Integer, primary_key=True)
    album_id = Column(Integer, ForeignKey("album.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    number = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    fcc_status = Column(Integer, nullable=False)
    last_played = Column(DateTime, nullable=False)
    times_played = Column(Integer, nullable=False)
    recommended = Column(Boolean, nullable=False)

    album = relationship("klap4.db_entities.album.Album", back_populates="songs")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"])

            kwargs["album_id"] = find_album_id(decomposed_tag.genre_abbr, decomposed_tag.artist_num, decomposed_tag.album_letter)

            if decomposed_tag.song_num is not None:
                kwargs["number"] = decomposed_tag.song_num

            kwargs.pop("id")

        if "number" not in kwargs:
            from klap4.db_entities import get_entity_from_tag
            album = get_entity_from_tag(f"{kwargs['genre_abbr']}{kwargs['artist_num']}{kwargs['album_letter']}")
            kwargs["number"] = len(album.songs) + 1

        if "fcc_status" not in kwargs:
            kwargs["fcc_status"] = Song.FCC_STATUS.UNRATED

        if "times_played" not in kwargs:
            kwargs["times_played"] = 0

        if "recommended" not in kwargs:
            kwargs["recommended"] = False

        if "last_played" not in kwargs:
            kwargs["last_played"] = datetime.fromtimestamp(0)

        super().__init__(**kwargs)

    @property
    def ref(self):
        return self.album.ref + str(self.number)

    def __repr__(self):
        return f"<Song(ref={self.ref}, " \
                     f"name={self.name}, " \
                     f"fcc_status={self.fcc_status}, " \
                     f"last_played={self.last_played}, " \
                     f"times_played={self.times_played}, " \
                     f"recommended={self.recommended})>"
