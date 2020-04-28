#!/usr/bin/env python3

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import backref, relationship

import klap4.db
from klap4.db_entities import SQLBase


class Genre(SQLBase):
    __tablename__ = "genre"

    id = Column(Integer, primary_key=True)
    abbreviation = Column(String(3), nullable=False, unique=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)

    artists = relationship("klap4.db_entities.artist.Artist", back_populates="genre", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            kwargs["abbreviation"] = kwargs["id"]

            kwargs.pop("id")

        super().__init__(**kwargs)

    @property
    def next_artist_num(self):
        return len(self.artists) + 1

    @property
    def ref(self):
        return self.abbreviation

    def __repr__(self):
        return f"<Genre(id={self.ref}, " \
                      f"name={self.name}, " \
                      f"color={self.color}, " \
                      f"next_artist_num={self.next_artist_num})>"
    
    def __str__(self):
        return self.abbreviation
