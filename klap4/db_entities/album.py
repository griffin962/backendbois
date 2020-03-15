#!/usr/bin/env python3

from datetime import datetime

from sqlalchemy import Column, ForeignKey, Boolean, DateTime, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class Album(SQLBase):
    __tablename__ = "album"

    class FORMAT:
        VINYL = 1 * 2 ** 0
        CD = 1 * 2 ** 1
        DIGITAL = 1 * 2 ** 2

    genre_abbr = Column(String(2), ForeignKey("genre.abbreviation"), primary_key=True)
    artist_num = Column(Integer, ForeignKey("artist.number"), primary_key=True)
    letter = Column(String(1), primary_key=True)
    name = Column(String, nullable=False)
    date_added = Column(DateTime, nullable=False)
    missing = Column(Boolean, nullable=False)
    is_new = Column(Boolean, nullable=False)
    format_bitfield = Column(Integer, nullable=False)
    label_id = Column(Integer, ForeignKey("label.id"), nullable=True)
    promoter_id = Column(Integer, ForeignKey("promoter.id"), nullable=True)

    label = relationship("klap4.db_entities.label_and_promoter.Label", back_populates="artists")
    promoter = relationship("klap4.db_entities.label_and_promoter.Promoter", back_populates="artists")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            kwargs["genre_abbr"] = kwargs["id"][:2]
            kwargs["artist_num"] = int(kwargs["id"][2:-1])

            if kwargs["id"][-1].isdigit():
                try:
                    kwargs.pop("letter")
                except KeyError:
                    pass
            else:
                kwargs["letter"] = kwargs["id"][-1]

        if "letter" not in kwargs:
            from klap4.db_entities import Artist
            kwargs["letter"] = klap4.db.Session().query(Artist) \
                .filter_by(genre_abbr=kwargs["genre_abbr"], number=kwargs["artist_num"]) \
                .first().next_album_letter

        defaults = {
            "date_added": datetime.now(),
            "missing": False,
            "is_new": False
        }
        for key, default in defaults.items():
            if key not in kwargs:
                kwargs[key] = default

        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Album(id={self.genre_abbr + str(self.artist_num) + self.letter}, " \
                      f"{self.name=}, " \
                      f"{self.date_added=}, " \
                      f"{self.missing=}, " \
                      f"{self.is_new=}, " \
                      f"format={self.format_bitfield}, " \
                      f"{self.label_id=}, " \
                      f"{self.promoter_id=})>"
