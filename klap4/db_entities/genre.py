#!/usr/bin/env python3

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class Genre(SQLBase):
    __tablename__ = "genre"

    abbreviation = Column(String(3), primary_key=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)

    next_artist_num = 0
    id = None

    # Relationships:

    # artists
    # albums
    # songs


    album_reviews = relationship("klap4.db_entities.album.AlbumReview", back_populates="genre",
                                 cascade="save-update, merge, delete")
    album_problems = relationship("klap4.db_entities.album.AlbumProblem", back_populates="genre",
                                  cascade="save-update, merge, delete")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            kwargs["abbreviation"] = kwargs["id"]

            kwargs.pop("id")

        super().__init__(**kwargs)

    @property
    def next_artist_num(self):
        return len(self.artists) + 1

    @property
    def id(self):
        return self.abbreviation

    def __repr__(self):
        return f"<Genre(id={self.id}, " \
                      f"name={self.name}, " \
                      f"color={self.color}, " \
                      f"next_artist_num={self.next_artist_num})>"
    
    def __str__(self):
        return self.abbreviation
