#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class Artist(SQLBase):
    __tablename__ = "artist"

    genre_abbr = Column(String(2), ForeignKey("genre.abbreviation"), primary_key=True)
    number = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    next_album_letter = None
    id = None

    genre = relationship("klap4.db_entities.genre.Genre", back_populates="artists")
    albums = relationship("klap4.db_entities.album.Album", back_populates="artist")
    album_reviews = relationship("klap4.db_entities.album.AlbumReview", back_populates="artist")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            kwargs["genre_abbr"] = kwargs["id"][:2]
            if len(kwargs["id"]) == 2:
                try:
                    kwargs.pop("number")
                except KeyError:
                    pass
            else:
                kwargs["number"] = int(kwargs["id"][2:])

        if "number" not in kwargs:
            kwargs["number"] = self.genre.next_artist_num
        super().__init__(**kwargs)

    @property
    def next_album_letter(self):
        return chr(ord('A') + len(self.albums))  # TODO: Handle letter wrap around ('Z' -> 'AA')

    @property
    def id(self):
        return self.genre.id + str(self.number)

    def __repr__(self):
        return f"<Artist(id={self.id}, " \
                       f"{self.name=}, " \
                       f"{self.next_album_letter=})>"
