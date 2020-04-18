#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import decompose_tag, full_module_name, SQLBase


class Artist(SQLBase):
    __tablename__ = "artist"

    genre_abbr = Column(String(2), ForeignKey("genre.abbreviation"), primary_key=True)
    number = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    next_album_letter = None
    id = None

    genre = relationship("klap4.db_entities.genre.Genre", back_populates="artists",
                         cascade="save-update, merge, delete")
    albums = relationship("klap4.db_entities.album.Album", back_populates="artist",
                          cascade="save-update, merge, delete")
    album_reviews = relationship("klap4.db_entities.album.AlbumReview", back_populates="artist",
                                 cascade="save-update, merge, delete")
    album_problems = relationship("klap4.db_entities.album.AlbumProblem", back_populates="artist",
                                  cascade="save-update, merge, delete")
    songs = relationship("klap4.db_entities.song.Song", back_populates="artist",
                         cascade="save-update, merge, delete")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"])
            kwargs["genre_abbr"] = decomposed_tag.genre_abbr

            if decomposed_tag.artist_num is not None:
                kwargs["number"] = decomposed_tag.artist_num

            kwargs.pop("id")

        if "number" not in kwargs:
            from klap4.db_entities import get_entity_from_tag
            genre = get_entity_from_tag(kwargs["genre_abbr"])
            kwargs["number"] = genre.next_artist_num

        super().__init__(**kwargs)

    @property
    def next_album_letter(self):
        return chr(ord('A') + len(self.albums))  # TODO: Handle letter wrap around ('Z' -> 'AA')
        # 'A' + 3 == 'D'

    @property
    def id(self):
        return self.genre.id + str(self.number)

    def __repr__(self):
        return f"<Artist(id={self.id}, " \
                       f"name={self.name}, " \
                       f"next_album_letter={self.next_album_letter})>"
