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
            from klap4.db_entities import Genre
            try:
                kwargs["number"] = klap4.db.Session().query(Genre) \
                    .filter_by(abbreviation=kwargs["genre_abbr"]) \
                    .first().next_artist_num
            except AttributeError as e:
                raise AttributeError(f"Genre '{kwargs['genre_abbr']}' does not exist.") from e
        super().__init__(**kwargs)

    @property
    def next_album_letter(self):
        from klap4.db_entities import Album
        count = klap4.db.Session().query(Album).filter_by(genre_abbr=self.genre_abbr, artist_num=self.number).count()
        return chr(ord('A') + count)  # TODO: Handle letter wrap around ('Z' -> 'AA')

    @property
    def id(self):
        return self.genre_abbr + str(self.number)

    def __repr__(self):
        return f"<Artist(id={self.id}, " \
                       f"{self.name=}, " \
                       f"{self.next_album_letter=})>"
