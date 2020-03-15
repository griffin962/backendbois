#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class Genre(SQLBase):
    __tablename__ = "genre"

    abbreviation = Column(String(2), primary_key=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    next_artist_num = 0

    artists = relationship("klap4.db_entities.artist.Artist", back_populates="genre")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def next_artist_num(self):
        from klap4.db_entities import Artist
        return klap4.db.Session().query(Artist).filter_by(genre_abbr=self.abbreviation).count() + 1

    def __repr__(self):
        return f"<Genre(id={self.abbreviation}, " \
                      f"{self.name=}, " \
                      f"{self.color=}, " \
                      f"{self.next_artist_num=})>"
