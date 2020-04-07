#!/usr/bin/env python3

from datetime import datetime, timedelta

from sqlalchemy import Column, ForeignKey, Boolean, DateTime, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import decompose_tag, SQLBase


class Song(SQLBase):
    __tablename__ = "song"

    class FCC_STATUS:
        UNRATED = 0
        CLEAN = 1
        INDECENT = 2
        OBSCENE = 3

    genre_abbr = Column(String(2), ForeignKey("genre.abbreviation"), primary_key=True)
    artist_num = Column(Integer, ForeignKey("artist.number"), primary_key=True)
    album_letter = Column(String(1), ForeignKey("album.letter"), primary_key=True)
    number = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    fcc_status = Column(Integer, nullable=False)
    last_played = Column(DateTime, nullable=False)
    times_played = Column(Integer, nullable=False)
    recommended = Column(Boolean, nullable=False)

    genre = relationship("klap4.db_entities.genre.Genre", back_populates="songs")
    artist = relationship("klap4.db_entities.artist.Artist", back_populates="songs")
    album = relationship("klap4.db_entities.album.Album", back_populates="songs")

    id = None

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"])
            kwargs["genre_abbr"] = decomposed_tag.genre_abbr
            kwargs["artist_num"] = decomposed_tag.artist_num
            kwargs["album_letter"] = decomposed_tag.album_letter

            if decomposed_tag.song_num is not None:
                kwargs["number"] = decomposed_tag.song_num

            kwargs.pop("id")

        if "number" not in kwargs:
            kwargs["number"] = len(self.album.songs) + 1

        super().__init__(**kwargs)

    @property
    def id(self):
        return self.album.id + str(self.number)

    def __repr__(self):
        return f"<Song(id={self.id}, " \
                     f"name={self.name}, " \
                     f"fcc_status={self.fcc_status}, " \
                     f"last_played={self.last_played}, " \
                     f"times_played={self.times_played}, " \
                     f"recommended={self.recommended})>"
