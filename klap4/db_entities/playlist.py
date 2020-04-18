#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase, decompose_tag
from klap4.utils import *


class Playlist(SQLBase):
    __tablename__ = "playlist"

    dj_id = Column(String, ForeignKey("dj.id"), primary_key=True)
    name = Column(String, primary_key=True)
    show = Column(String, nullable=False)

    dj = relationship("klap4.db_entities.dj.DJ", back_populates="playlists", cascade="save-update, merge, delete")
    entries = relationship("klap4.db_entities.playlist.PlaylistEntry", back_populates="playlist",
                           cascade="save-update, merge, delete")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"], regex_hint="playlist")

            kwargs["dj_id"] = decomposed_tag.dj_id
            kwargs["name"] = decomposed_tag.name

            kwargs.pop("id")

        super().__init__(**kwargs)

    @property
    def id(self):
        return f"{self.dj.id}+{self.name}"

    def __repr__(self):
        return f"<Playlist(id={self.id}, " \
                         f"show={self.show})>"


class PlaylistEntry(SQLBase):
    __tablename__ = "playlist_entry"

    dj_id = Column(String, ForeignKey("dj.id"), primary_key=True)
    playlist_name = Column(String, ForeignKey("playlist.name"), primary_key=True)
    index = Column(Integer, primary_key=True)
    reference_type = Column(Integer, nullable=False)
    reference = Column(String, nullable=False)

    dj = relationship("klap4.db_entities.dj.DJ", back_populates="playlist_entries",
                      cascade="save-update, merge, delete")
    playlist = relationship("klap4.db_entities.playlist.Playlist", back_populates="entries",
                            cascade="save-update, merge, delete")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"], regex_hint="playlist")

            kwargs["dj_id"] = decomposed_tag.dj_id
            kwargs["playlist_name"] = decomposed_tag.name

            if decomposed_tag.song_num is not None:
                kwargs["index"] = decomposed_tag.song_num

            kwargs.pop("id")

        if "index" not in kwargs:
            from klap4.db_entities import get_entity_from_tag
            playlist = get_entity_from_tag(f"{kwargs['dj_id']}+{kwargs['playlist_name']}")
            kwargs["index"] = len(playlist.playlist_entries) + 1

            print(playlist)

        kwargs["reference"] = normalize_metadata[kwargs["reference_type"]](kwargs["reference"])

        super().__init__(**kwargs)

    def get_song_data(self) -> json:
        try:
            return get_metadata[self.reference_type](self.reference)
        except KeyError as e:
            raise KeyError(f"No playlist reference type '{self.reference_type}'.") from e

    @property
    def id(self):
        return f"{self.playlist.id}+{self.index}"

    @property
    def in_library(self):
        return self.reference_type == REFERENCE_TYPE.IN_KLAP4

    def __repr__(self):
        return f"<PlaylistEntry(id={self.id}, " \
                              f"reference_type={self.reference_type}, " \
                              f"reference={self.reference[:20] + '...' if len(self.reference) > 20 else self.reference})>"
