from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

from klap4.db_entities import SQLBase, decompose_tag
from klap4.db_entities.playlist import Playlist, PlaylistEntry
from klap4.utils import *

def list_playlists(user: str) -> list:
    from klap4.db import Session
    session = Session()

    playlists = session.query(Playlist) \
        .filter(Playlist.dj_id == user).all()
    
    return format_object_list(playlists)


def add_playlist(user: str, name: str, show: str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    newPlaylist = Playlist(dj_id=user,
                                playlist_name=name,
                                show=show)
    
    session.add(newPlaylist)
    session.commit()

    return newPlaylist

def update_playlist(user: str, name: str, show:str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    update = Playlist.update(). \
                        where(Playlist.dj_id == user). \
                        values(playlist_name=name, show=show)
    
    return update


def delete_playlist(user: str, name: str) -> None:
    from klap4.db import Session
    session = Session()

    session.query(Playlist).filter(and_(Playlist.dj_id == user, Playlist.playlist_name == name)).delete()

    return


def display_playlist(dj_id: str, p_name: str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    info_list = []

    playlist = session.query(Playlist) \
        .filter(and_(Playlist.dj_id == dj_id, Playlist.playlist_name == p_name)).one()
    
    playlist_entries = session.query(PlaylistEntry) \
        .filter(and_(PlaylistEntry.dj_id == dj_id, PlaylistEntry.playlist_name == p_name)).all()
    info_list.append(playlist_entries)

    for sublist in info_list:
        format_object_list(sublist)

    info_list.append(get_json(playlist))

    return info_list


def add_playlist_entry(user: str, p_name: str, song: str, artist: str, album: str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    newPlaylistEntry = PlaylistEntry(
        dj_id=user, 
        playlist_name=p_name, 
        song_name=song, 
        artist_name=artist, 
        album_name=album)
    
    session.add(newPlaylistEntry)
    session.commit()

    return newPlaylistEntry


def update_playlist_entry(user: str, p_name: str, song: str, artist: str, album: str, new_song: str, new_artist: str, new_album: str):
    from klap4.db import Session
    session = Session()
    
    update = PlaylistEntry.update(). \
                where(
                    and_(
                        PlaylistEntry.dj_id == user, 
                        PlaylistEntry.playlist_name == p_name,
                        PlaylistEntry.song_name == song,
                        PlaylistEntry.artist_name == artist,
                        PlaylistEntry.album_name == album
                    )
                ). \
                values(song_name=new_song, artist_name=new_artist, album_name=new_album)
    
    return update


def delete_playlist_entry(user: str, p_name: str, song: str, artist: str, album: str) -> None:
    from klap4.db import Session
    session = Session()

    session.query(PlaylistEntry).filter(and_(
        PlaylistEntry.dj_id == user, 
        PlaylistEntry.playlist_name == p_name, 
        PlaylistEntry.song_name == song, 
        PlaylistEntry.artist_name == artist, 
        PlaylistEntry.album_name == album)).delete()
    
    return
