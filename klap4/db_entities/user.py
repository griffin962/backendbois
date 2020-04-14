#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import decompose_tag, full_module_name, SQLBase


class User(SQLBase):
    __tablename__ = "user"

    #initialize playlist variables
    username = Column(String, primary_key=True))


    #table relations
    playlists = relationship("klap4.db_entities.playlist.Playlist", back_populates="user")


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    #output representation
    def __repr__(self):
        return f"<Artist(username={self.username}, ")>"
