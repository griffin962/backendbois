#!/usr/bin/env python3

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class Genre(SQLBase):
    __tablename__ = "genre"

    abbreviation = Column(String(2), primary_key=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    next_artist_num = 0
    id = None

    artists = relationship("klap4.db_entities.artist.Artist", back_populates="genre")
    albums = relationship("klap4.db_entities.album.Album", back_populates="genre")
    album_reviews = relationship("klap4.db_entities.album.AlbumReview", back_populates="genre")
    songs = relationship("klap4.db_entities.song.Song", back_populates="genre")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def next_artist_num(self):
        return len(self.artists) + 1

    @property
    def id(self):
        return self.abbreviation

    def __repr__(self):
        return f"<Genre(id={self.id}, " \
                      f"{self.name=}, " \
                      f"{self.color=}, " \
                      f"{self.next_artist_num=})>"
