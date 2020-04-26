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
                                name=name,
                                show=show)
    
    session.add(newPlaylist)
    session.commit()

    return newPlaylist

def update_playlist(user: str, name: str, show:str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    update = Playlist.update(). \
                        where(Playlist.dj_id == user). \
                        values(name=name, show=show)
    session.commit()
    return update


def delete_playlist(user: str, name: str) -> None:
    from klap4.db import Session
    session = Session()

    session.query(Playlist).filter(and_(Playlist.dj_id == user, Playlist.name == name)).delete()
    session.commit()

    return


def display_playlist(dj_id: str, p_name: str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    try:
        u_playlist = session.query(Playlist) \
            .filter(and_(Playlist.dj_id == dj_id, Playlist.name == p_name)).one()
    except:
        return {"error": "ERROR"}
    
    playlist = get_json(u_playlist)
    
    playlist_entries = session.query(PlaylistEntry) \
        .filter(and_(PlaylistEntry.dj_id == dj_id, PlaylistEntry.playlist_name == p_name)).all()

    info_list = format_object_list(playlist_entries)

    obj = {
            "playlist": playlist,
            "playlist_entries": info_list
    }

    return obj


def add_playlist_entry(user: str, p_name: str, index: int, entry) -> SQLBase:
    from klap4.db import Session
    session = Session()

    newPlaylistEntry = PlaylistEntry(
        dj_id=user, 
        playlist_name=p_name, 
        index=index,
        entry=entry)
    
    session.add(newPlaylistEntry)
    session.commit()

    return newPlaylistEntry


def update_playlist_entry(user: str, p_name: str, index: int, entry, new_index: int, new_entry):
    from klap4.db import Session
    session = Session()

    session.update(PlaylistEntry) \
        .filter(
            and_(PlaylistEntry.dj_id == user, PlaylistEntry.playlist_name == p_name,
                 PlaylistEntry.index == index, PlaylistEntry.entry == entry)
        ) \
        .update({PlaylistEntry.index:new_index, PlaylistEntry.entry:new_entry}, synchronize_session=False)
    
    session.commit()
    
    return


def delete_playlist_entry(user: str, p_name: str, index: int, entry) -> None:
    from klap4.db import Session
    session = Session()

    session.query(PlaylistEntry).filter(and_(
        PlaylistEntry.dj_id == user, 
        PlaylistEntry.playlist_name == p_name, 
        PlaylistEntry.index == index,
        PlaylistEntry.entry)).delete()
    
    session.commit()
    
    return
