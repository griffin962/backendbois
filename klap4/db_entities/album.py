#!/usr/bin/env python3

from datetime import datetime, timedelta

from sqlalchemy import Column, ForeignKey, Boolean, DateTime, String, Integer, UniqueConstraint
from sqlalchemy.orm import backref, relationship

import klap4.db
from klap4.db_entities import decompose_tag, full_module_name, SQLBase


class Album(SQLBase):
    __tablename__ = "album"

    class FORMAT:
        VINYL = 0b00001
        CD = 0b00010
        DIGITAL =0b00100
        SINGLE = 0b01000
        SEVENINCH = 0b10000

    genre_abbr = Column(String(2), ForeignKey("genre.abbreviation"), primary_key=True)
    artist_num = Column(Integer, ForeignKey("artist.number"), primary_key=True)
    letter = Column(String(1), primary_key=True)
    name = Column(String, nullable=False)
    date_added = Column(DateTime, nullable=False)
    missing = Column(Boolean, nullable=False)
    format_bitfield = Column(Integer, nullable=False)
    label_id = Column(Integer, ForeignKey("label.id"), nullable=True)
    promoter_id = Column(Integer, ForeignKey("promoter.id"), nullable=True)

    genre = relationship("klap4.db_entities.genre.Genre", 
                         back_populates="albums",
                         uselist=False,
                         primaryjoin="Genre.abbreviation == Album.genre_abbr")

    artist = relationship("klap4.db_entities.artist.Artist",
                          back_populates="albums",
                          uselist=False,
                          primaryjoin="and_("
                                      "     Artist.genre_abbr == Album.genre_abbr,"
                                      "     Artist.number == Album.artist_num"
                                      ")")
    
    reviews = relationship("klap4.db_entities.album.AlbumReview", back_populates="album", cascade="all, delete-orphan")
    problems = relationship("klap4.db_entities.album.AlbumProblem", back_populates="album", cascade="all, delete-orphan")
    songs = relationship("klap4.db_entities.song.Song", back_populates="album", cascade="all, delete-orphan")
    label = relationship("klap4.db_entities.label_and_promoter.Label", back_populates="albums")
    promoter = relationship("klap4.db_entities.label_and_promoter.Promoter", back_populates="albums")

    __table_args__ = (UniqueConstraint('genre_abbr', 'artist_num', 'letter'),)

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
    dj_id = Column(String, ForeignKey("dj.id"), primary_key=True)
    date_entered = Column(DateTime, nullable=False)
    content = Column(String, nullable=False)

    genre = relationship("klap4.db_entities.genre.Genre",
                         back_populates="reviews",
                         primaryjoin="Genre.abbreviation == AlbumReview.genre_abbr")
    
    artist = relationship("klap4.db_entities.artist.Artist",
                          back_populates="reviews",
                          primaryjoin="and_("
                                      "     Artist.genre_abbr == AlbumReview.genre_abbr,"
                                      "     Artist.number == AlbumReview.artist_num"
                                      ")")
    
    album = relationship("klap4.db_entities.album.Album",
                         back_populates="reviews",
                         primaryjoin="and_("
                                     "     Album.genre_abbr == AlbumReview.genre_abbr,"
                                     "     Album.artist_num == AlbumReview.artist_num,"
                                     "     Album.letter == AlbumReview.album_letter"
                                     ")")
    
    dj = relationship("klap4.db_entities.dj.DJ", back_populates="reviews")

    def __init__(self, **kwargs):
        if "date_entered" in kwargs:
            kwargs["date_entered"] = datetime.now()
        super().__init__(**kwargs)

    @property
    def is_recent(self):
        return datetime.now() - self.date_entered < timedelta(weeks=4)

    @property
    def id(self):
        return self.album.id + str(self.dj_id)

    def __repr__(self):
        return f"<AlbumReview(id={self.id}, " \
                            f"date_entered={self.date_entered}, " \
                            f"is_recent={self.is_recent}, " \
                            f"content={self.content[:20] + '...' if len(self.content) > 20 else self.content})>"


class AlbumProblem(SQLBase):
    __tablename__ = "album_problem"

    genre_abbr = Column(String(2), ForeignKey("genre.abbreviation"), primary_key=True)
    artist_num = Column(Integer, ForeignKey("artist.number"), primary_key=True)
    album_letter = Column(String(1), ForeignKey("album.letter"), primary_key=True)
    dj_id = Column(String, ForeignKey("dj.id"), primary_key=True)
    content = Column(String, nullable=False)

    genre = relationship("klap4.db_entities.genre.Genre",
                         back_populates="problems",
                         primaryjoin="Genre.abbreviation == AlbumProblem.genre_abbr")
    
    artist = relationship("klap4.db_entities.artist.Artist",
                          back_populates="problems",
                          primaryjoin="and_("
                                      "     Artist.genre_abbr == AlbumProblem.genre_abbr,"
                                      "     Artist.number == AlbumProblem.artist_num"
                                      ")")
    
    album = relationship("klap4.db_entities.album.Album",
                         back_populates="problems",
                         primaryjoin="and_("
                                     "     Album.genre_abbr == AlbumProblem.genre_abbr,"
                                     "     Album.artist_num == AlbumProblem.artist_num,"
                                     "     Album.letter == AlbumProblem.album_letter"
                                     ")")
    
    dj = relationship("klap4.db_entities.dj.DJ", back_populates="problems")

    @property
    def id(self):
        return f"{self.album.id}!{self.dj_id}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<AlbumProblem(id={self.id}, " \
                             f"content={self.content[:20] + '...' if len(self.content) > 20 else self.content})>"
