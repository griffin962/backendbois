from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

from klap4.db_entities import SQLBase, decompose_tag
from klap4.db_entities.album import Album
from klap4.db_entities.artist import Artist
from klap4.db_entities.dj import DJ
from klap4.db_entities.playlist import Playlist, PlaylistEntry
from klap4.db_entities.song import Song
from klap4.utils import *

def list_playlists(dj_id: str) -> list:
    from klap4.db import Session
    session = Session()

    playlists = session.query(Playlist) \
        .filter(Playlist.dj_id == dj_id).all()
    
    return format_object_list(playlists)


def add_playlist(dj_id: str, name: str, show: str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    new_playlist = Playlist(dj_id=dj_id,
                                name=name,
                                show=show)
    
    session.add(new_playlist)
    session.commit()

    return new_playlist

def update_playlist(dj_id: str, name: str, show: str, new_name: str, new_show: str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    playlist_update = session.query(Playlist) \
        .filter(
            and_(Playlist.dj_id == dj_id, Playlist.name == name)
        ) \
        .one()
    
    playlist_update.name = new_name
    playlist_update.show = new_show

    session.commit()
    return playlist_update


def delete_playlist(dj_id: str, name: str) -> None:
    from klap4.db import Session
    session = Session()

    session.query(Playlist).filter(and_(Playlist.dj_id == dj_id, Playlist.name == name)).delete()
    session.commit()

    return


def display_playlist_entries(dj_id: str, p_name: str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    try:
        u_playlist = session.query(Playlist) \
            .filter(and_(Playlist.dj_id == dj_id, Playlist.name == p_name)).one()
    except:
        return {"error": "ERROR"}
    
    playlist = get_json(u_playlist)
    
    playlist_entries = session.query(PlaylistEntry) \
        .join(Playlist, and_(Playlist.id == PlaylistEntry.playlist_id, Playlist.name == p_name)) \
        .join(DJ, and_(DJ.id == Playlist.dj_id, DJ.id == dj_id)) \
        .order_by(PlaylistEntry.index) \
        .all()

    info_list = format_object_list(playlist_entries)

    obj = {
            "playlist": playlist,
            "playlist_entries": info_list
    }

    return obj


def add_playlist_entry(dj_id: str, p_name: str, entry) -> SQLBase:
    from klap4.db import Session
    session = Session()

    from datetime import datetime
    try:
        song_entry = session.query(Song) \
                        .join(Album, and_(Album.id == Song.album_id, Album.name == entry["album"])) \
                        .join(Artist, and_(Artist.id == Album.artist_id, Artist.name == entry["artist"])) \
                        .filter(Song.name == entry["song"]).one()
        
        old_times_played = song_entry.times_played
        song_entry.last_played = datetime.now()
        session.commit()
        song_entry.times_played = old_times_played + 1
        session.commit()

        reference_type = REFERENCE_TYPE.IN_KLAP4
        reference = song_entry.album.artist.genre.abbreviation + str(song_entry.album.artist.number) + song_entry.album.letter
    except:
        reference_type = REFERENCE_TYPE.MANUAL
        reference = str(entry)


    newPlaylistEntry = PlaylistEntry(
        dj_id=dj_id, 
        playlist_name=p_name, 
        reference=reference,
        reference_type=reference_type,
        entry=entry)
    
    session.add(newPlaylistEntry)
    session.commit()

    return get_json(newPlaylistEntry)


def update_playlist_entry(dj_id: str, p_name: str, index: int, entry, new_index: int, new_entry):
    from klap4.db import Session
    session = Session()

    from datetime import datetime

    if new_index is None and entry is not None and new_entry is not None:
        try:
            song_entry = session.query(Song) \
                        .join(Album, and_(Album.id == Song.album_id, Album.name == entry["album"])) \
                        .join(Artist, and_(Artist.id == Album.artist_id, Artist.name == entry["artist"])) \
                        .filter(Song.name == entry["song"]).one()
            old_times_played = song_entry.times_played

            song_entry.last_played = datetime.now()
            session.commit()
            song_entry.times_played = old_times_played + 1
            session.commit()

            reference_type = REFERENCE_TYPE.IN_KLAP4
            reference = song_entry.album.artist.genre.abbreviation + str(song_entry.album.artist.number) + song_entry.album.letter
        except:
            reference_type = REFERENCE_TYPE.MANUAL
            reference = str(new_entry)
        
        update_entry = session.query(PlaylistEntry) \
            .join(Playlist, and_(Playlist.id == PlaylistEntry.id, Playlist.name == p_name)) \
            .join(DJ, and_(DJ.id == Playlist.dj_id, DJ.id == dj_id)) \
            .filter(
                and_(PlaylistEntry.index == index,
                     PlaylistEntry.entry == entry)
            ) \
            .one()
        
        update_entry.entry = new_entry
        update_entry.reference = reference
        update_entry.reference_type = reference_type
        session.commit()
    
    else:
        old_index = index
        playlist_entries = session.query(PlaylistEntry) \
            .join(Playlist, and_(Playlist.id == PlaylistEntry.playlist_id, Playlist.name == p_name)) \
            .join(DJ, and_(DJ.id == Playlist.dj_id, DJ.id == dj_id)) \
            .order_by(PlaylistEntry.index) \
            .all()
        
        if new_index > old_index:
            playlist_entries[old_index-1].index = -1
            for entry in playlist_entries[old_index:new_index]:
                entry.index = entry.index - 1
            
            session.commit()
            playlist_entries[old_index-1].index = new_index
            session.commit()


        elif new_index < old_index:
            playlist_entries[new_index-1].index = -1

            playlist_entries[old_index-1].index = new_index
            session.commit()
            
            for num in range(old_index-1, new_index, -1):
                playlist_entries[num-1].index = playlist_entries[num-1].index + 1
                session.commit()
            
            session.commit()
            playlist_entries[new_index-1].index = new_index+1
            session.commit()
        
        else:
            pass

    return
    


def delete_playlist_entry(dj_id: str, p_name: str, index: int) -> None:
    from klap4.db import Session
    session = Session()

    playlist_entries = session.query(PlaylistEntry) \
            .join(Playlist, and_(Playlist.id == PlaylistEntry.playlist_id, Playlist.name == p_name)) \
            .join(DJ, and_(DJ.id == Playlist.dj_id, DJ.id == dj_id)) \
            .order_by(PlaylistEntry.index) \
            .all()

    to_delete = session.query(PlaylistEntry) \
        .join(Playlist, and_(Playlist.id == PlaylistEntry.playlist_id, Playlist.name == p_name)) \
        .join(DJ, and_(DJ.id == Playlist.dj_id, DJ.id == dj_id)) \
        .filter(PlaylistEntry.index == index) \
        .one()
    
    to_delete.index = -1

    for entry in playlist_entries[index:]:
        entry.index = entry.index - 1
    
    session.commit()
    session.delete(to_delete)
    session.commit()
    
    return
