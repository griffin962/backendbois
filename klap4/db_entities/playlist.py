#!/usr/bin/env python3

from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

import klap4.db
from klap4.db_entities import SQLBase


class Playlist(SQLBase):
    __tablename__ = "playlist"

    dj_id = Column(String, ForeignKey("dj.dj_id"), primary_key=True)
    playlist_name = Column(String, primary_key=True)
    show = Column(String, nullable=True)

    dj = relationship("klap4.db_entities.dj.DJ", back_populates="playlists")
    playlist_entries = relationship("klap4.db_entities.playlist.PlaylistEntry", back_populates="playlist")


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    @property
    def id(self):
        return str(self.dj_id) + str(self.playlist_name)

    
    def __repr__(self):
        return f"<Playlist(dj_id={self.dj_id}, " \
                        f"playlist_name={self.playlist_name}, " \
                        f"show={self.show})>"


class PlaylistEntry(SQLBase):
    __tablename__ = "playlist_entry"

    dj_id = Column(String, ForeignKey("dj.dj_id"), primary_key=True)
    playlist_name = Column(String, ForeignKey("playlist.playlist_name"), primary_key=True)
    song_name = Column(String, primary_key=True)
    artist_name = Column(String, primary_key=True)
    album_name = Column(String, primary_key=True)
    
    dj = relationship("klap4.db_entities.dj.DJ", back_populates="playlist_entries")
    playlist = relationship("klap4.db_entities.playlist.Playlist", back_populates="playlist_entries")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    

    @property
    def id(self):
        return str(self.dj_id) + str(self.playlist_name) + str(self.song_name) + str(self.artist_name) + str(self.album_name)
    

    # Will need to be updated
    @property
    def in_library(self):
        return True
    

    def __repr__(self):
        return f"<PlaylistEntry(dj_id={self.dj_id}, " \
                        f"playlist_name={self.playlist_name}, " \
                        f"song_name={self.song_name}, " \
                        f"artist_name={self.artist_name}, " \
                        f"album_name={self.album_name})>"