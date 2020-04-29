#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, UniqueConstraint, String, Integer, JSON
from sqlalchemy.orm import backref, relationship

import klap4.db
from klap4.db_entities import SQLBase, decompose_tag
from klap4.db_entities.dj import DJ
from klap4.utils import *


def find_playlist_id(dj_id: str, playlist_name: str):
    entity = None

    try:
        from klap4.db import Session
        session = Session()

        entity = session.query(Playlist) \
            .join(DJ, DJ.id == Playlist.dj_id) \
            .filter(Playlist.name == playlist_name).one()
        
        return entity.id
    except:
        raise "error"


class Playlist(SQLBase):
    __tablename__ = "playlist"
    __table_args__ = (UniqueConstraint('dj_id', 'name', name='playlist_constraint'),)

    id = Column(Integer, primary_key=True)
    dj_id = Column(String, ForeignKey("dj.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    show = Column(String, nullable=False)

    dj = relationship("klap4.db_entities.dj.DJ", back_populates="playlists")
    playlist_entries = relationship("klap4.db_entities.playlist.PlaylistEntry", back_populates="playlist", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"], regex_hint="playlist")

            kwargs["dj_id"] = decomposed_tag.dj_id
            kwargs["name"] = decomposed_tag.name

            kwargs.pop("id")

        super().__init__(**kwargs)

    @property
    def ref(self):
        return f"{self.dj_id}+{self.name}"

    def __repr__(self):
        return f"<Playlist(ref={self.ref}, " \
                         f"show={self.show})>"
    
    def __str__(self):
        return self.ref


class PlaylistEntry(SQLBase):
    __tablename__ = "playlist_entry"

    id = Column(Integer, primary_key=True)
    playlist_id = Column(Integer, ForeignKey("playlist.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    index = Column(Integer, nullable=False)
    reference_type = Column(Integer, nullable=False)
    reference = Column(String, nullable=False)
    entry = Column(JSON, nullable=False)
    
    playlist = relationship("klap4.db_entities.playlist.Playlist", back_populates="playlist_entries")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"], regex_hint="playlist")

            kwargs["playlist_id"] = find_playlist_id(decomposed_tag.dj_id, decomposed_tag.name)

            if decomposed_tag.song_num is not None:
                kwargs["index"] = decomposed_tag.song_num

            kwargs.pop("id")

        if "index" not in kwargs:
            from klap4.db_entities import get_entity_from_tag
            playlist = get_entity_from_tag(f"{kwargs['dj_id']}+{kwargs['playlist_name']}")
            kwargs["index"] = len(playlist.playlist_entries) + 1
            kwargs["playlist_id"] = playlist.id
            kwargs.pop("dj_id")
            kwargs.pop("playlist_name")

            print(playlist)

        #kwargs["reference"] = normalize_metadata[kwargs["reference_type"]](kwargs["reference"])

        super().__init__(**kwargs)

    def get_song_data(self) -> json:
        try:
            return get_metadata[self.reference_type](self.reference)
        except KeyError as e:
            raise KeyError(f"No playlist reference type '{self.reference_type}'.") from e

    @property
    def ref(self):
        return f"{self.playlist.ref}+{self.index}"

    @property
    def in_library(self):
        return self.reference_type == REFERENCE_TYPE.IN_KLAP4

    def __repr__(self):
        return f"<PlaylistEntry(ref={self.ref}, " \
                              f"reference_type={self.reference_type}, " \
                              f"reference={self.reference[:20] + '...' if len(self.reference) > 20 else self.reference})>"
