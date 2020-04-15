#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class Playlist(SQLBase):
    __tablename__ = "playlist"

    dj_id = Column(String, primary_key=True)
    playlist_name = Column(String, primary_key=True)
    show = Column(String, nullable=True)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    @property
    def id(self):
        return str(self.dj_id) + str(self.playlist_name)

    
    def __repr__(self):
        return f"<Playlist(dj_id={self.dj_id}, " \
                        f"playlist_name={self.playlist_name}, " \
                        f"show={self.show})>"