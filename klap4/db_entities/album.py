#!/usr/bin/env python3

from datetime import datetime, timedelta

from sqlalchemy import Column, ForeignKey, Boolean, DateTime, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import decompose_tag, full_module_name, SQLBase


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
    format_bitfield = Column(Integer, nullable=False)
    label_id = Column(Integer, ForeignKey("label.id"), nullable=True)
    promoter_id = Column(Integer, ForeignKey("promoter.id"), nullable=True)

    genre = relationship("klap4.db_entities.genre.Genre", back_populates="albums")
    artist = relationship("klap4.db_entities.artist.Artist", back_populates="albums")
    songs = relationship("klap4.db_entities.song.Song", back_populates="album")
    label = relationship("klap4.db_entities.label_and_promoter.Label", back_populates="artists")
    promoter = relationship("klap4.db_entities.label_and_promoter.Promoter", back_populates="artists")
    album_reviews = relationship("klap4.db_entities.album.AlbumReview", back_populates="album")

    is_new = False
    id = None

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"])
            kwargs["genre_abbr"] = decomposed_tag.genre_abbr
            kwargs["artist_num"] = decomposed_tag.artist_num

            if decomposed_tag.album_letter is not None:
                kwargs["letter"] = decomposed_tag.album_letter

            kwargs.pop("id")

        if "letter" not in kwargs:
            from klap4.db_entities import get_entity_from_tag
            artist = get_entity_from_tag(f"{kwargs['genre_abbr']}{kwargs['artist_num']}")
            kwargs["letter"] = artist.next_album_letter

        defaults = {
            "date_added": datetime.now(),
            "missing": False,
        }
        kwargs = {**defaults, **kwargs}

        super().__init__(**kwargs)

    @property
    def is_new(self):
        return datetime.now() - self.date_added < timedelta(days=30 * 6)

    @property
    def id(self):
        return self.artist.id + self.letter

    def __repr__(self):
        return f"<Album(id={self.id}, " \
                      f"name={self.name}, " \
                      f"date_added={self.date_added}, " \
                      f"missing={self.missing}, " \
                      f"is_new={self.is_new}, " \
                      f"format={self.format_bitfield}, " \
                      f"label_id={self.label_id}, " \
                      f"promoter_id={self.promoter_id})>"


class AlbumReview(SQLBase):
    __tablename__ = "album_review"

    genre_abbr = Column(String(2), ForeignKey("genre.abbreviation"), primary_key=True)
    artist_num = Column(Integer, ForeignKey("artist.number"), primary_key=True)
    album_letter = Column(String(1), ForeignKey("album.letter"), primary_key=True)
    dj_id = Column(String, primary_key=True)
    date_entered = Column(DateTime, nullable=False)
    content = Column(String, nullable=False)

    genre = relationship("klap4.db_entities.genre.Genre", back_populates="album_reviews")
    artist = relationship("klap4.db_entities.artist.Artist", back_populates="album_reviews")
    album = relationship("klap4.db_entities.album.Album", back_populates="album_reviews")

    is_recent = False
    id = False

    def __init__(self, **kwargs):
        if "date_entered" in kwargs:
            kwargs["date_entered"] = datetime.now()
        super().__init__(**kwargs)

    @property
    def is_recent(self):
        return datetime.now() - self.date_added < timedelta(weeks=4)

    @property
    def id(self):
        return self.album.id + str(self.dj_id)

    def __repr__(self):
        return f"<AlbumReview(id={self.id}, " \
                            f"date_entered={self.date_entered}, " \
                            f"is_recent={self.is_recent}, " \
                            f"content={self.content[:20] + '...' if len(self.content) > 20 else self.message})>"
