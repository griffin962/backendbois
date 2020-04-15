#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class DJ(SQLBase):
    __tablename__ = "dj"

    dj_id = Column(String, primary_key=True)
    is_admin = Column(Boolean, nullable=False)

    playlists = relationship("klap4.db_entities.playlist.Playlist", back_populates="dj")
    playlist_entries = relationship("klap4.db_entities.playlist.PlaylistEntry", back_populates="dj")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    

    @property
    def id(self):
        return str(self.dj_id) + str(self.is_admin)
    

    def __repr__(self):
        return f"<DJ(dj_id={self.dj_id}, is_admin={self.is_admin})>"