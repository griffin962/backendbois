#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import backref, relationship

import klap4.db
from klap4.db_entities import decompose_tag, full_module_name, SQLBase
#from klap4.utils.spotify_utils import getArtistImage, getRelatedArtists


class Artist(SQLBase):
    __tablename__ = "artist"

    genre_abbr = Column(String(2), ForeignKey("genre.abbreviation"), primary_key=True)
    number = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    genre = relationship("klap4.db_entities.genre.Genre", uselist=False, back_populates="artists")
    albums = relationship("klap4.db_entities.album.Album", back_populates="artist", uselist=True, cascade="all, delete-orphan",
                          primaryjoin="and_("
                                      "     Artist.genre_abbr == Album.genre_abbr,"
                                      "     Artist.number == Album.artist_num"
                                      ")")
    reviews = relationship("klap4.db_entities.album.AlbumReview", back_populates="artist",
                           primaryjoin="and_("
                                      "     Artist.genre_abbr == AlbumReview.genre_abbr,"
                                      "     Artist.number == AlbumReview.artist_num"
                                      ")")
    problems = relationship("klap4.db_entities.album.AlbumProblem", back_populates="artist",
                            primaryjoin="and_("
                                      "     Artist.genre_abbr == AlbumProblem.genre_abbr,"
                                      "     Artist.number == AlbumProblem.artist_num"
                                      ")")
    songs = relationship("klap4.db_entities.song.Song", back_populates="artist",
                         primaryjoin="and_("
                                      "     Artist.genre_abbr == Song.genre_abbr,"
                                      "     Artist.number == Song.artist_num"
                                      ")")

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
    

    def serialize(self):
        album_list = []
        for album in self.albums:
            album_list.append({
                                "id": album.id,
                                "album_name": album.name,
                                "album_format": album.format_bitfield,
                                "new_album": album.is_new,
                                "has_reviews": True if len(album.reviews) > 0 else False,
                                "has_problems": True if len(album.problems) > 0 else False,
                                "missing": album.missing
                            })

        serialized_artist = {
                                "id": self.id,
                                "name": self.name,
                                "genre": self.genre.name,
                                "albums": album_list,
                                #"image": getArtistImage(self.name)
                            }
        return serialized_artist

    def __repr__(self):
        return f"<Artist(id={self.id}, " \
                       f"name={self.name}, " \
                       f"next_album_letter={self.next_album_letter})>"

    def __str__(self):
        return self.name
