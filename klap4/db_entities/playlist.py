#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import decompose_tag, full_module_name, SQLBase


class Playlist(SQLBase):
    __tablename__ = "playlist"

    #initialize playlist variables
    username = column(String, ForeignKey("user.name"), primary_key=True)
    show = column(string, nullable=True)
    playlist_name = column(String, username + show, primary_key = True)
    #id= None


    #table relations
    username = column("klap4.db_entities.user.User", back_populates="playlist")


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    #output representation
    def __repr__(self):
        return f"<Artist(username={self.username}, " \
                       f"show={self.show}, " \
                       f"playlist_name={self.playlist_name})>"
