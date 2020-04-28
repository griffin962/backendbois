from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

from klap4.db_entities import SQLBase, decompose_tag
from klap4.db_entities.album import Album
from klap4.db_entities.artist import Artist
from klap4.db_entities.playlist import Playlist, PlaylistEntry
from klap4.db_entities.song import Song
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

def update_playlist(user: str, name: str, show: str, new_name: str, new_show: str) -> SQLBase:
    from klap4.db import Session
    session = Session()

    session.query(Playlist) \
        .filter(
            and_(Playlist.dj_id == user, Playlist.name == name)
        ) \
        .update({Playlist.name: new_name, Playlist.show: new_show}, synchronize_session=False)

    session.commit()
    return


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

    from datetime import datetime
    try:
        song_entry = session.query(Song) \
                        .join(Artist, and_(Artist.genre_abbr == Song.genre_abbr, 
                            Artist.number == Song.artist_num, 
                            Artist.name == entry["artist"])) \
                        .join(Album, and_(Album.genre_abbr == Song.genre_abbr, 
                            Album.artist_num == Song.artist_num, 
                            Album.letter == Song.album_letter, 
                            Album.name == entry["album"])) \
                        .filter(Song.name == entry["song"]).one()
        
        old_times_played = song_entry.times_played
        song_entry.last_played = datetime.now()
        session.commit()
        song_entry.times_played = old_times_played + 1
        session.commit()

        reference_type = REFERENCE_TYPE.IN_KLAP4
        reference = song_entry.genre_abbr + str(song_entry.artist_num) + song_entry.album_letter
    except:
        reference_type = REFERENCE_TYPE.MANUAL
        reference = str(entry)


    newPlaylistEntry = PlaylistEntry(
        dj_id=user, 
        playlist_name=p_name, 
        index=index,
        reference=reference,
        reference_type=reference_type,
        entry=entry)
    
    session.add(newPlaylistEntry)
    session.commit()

    return newPlaylistEntry


def update_playlist_entry(dj_id: str, p_name: str, index: int, entry, new_index: int, new_entry):
    from klap4.db import Session
    session = Session()

    from datetime import datetime

    if new_index is None and entry is not None and new_entry is not None:
        try:
            song_entry = session.query(Song) \
                            .join(Artist, and_(Artist.genre_abbr == Song.genre_abbr, 
                                Artist.number == Song.artist_num, 
                                Artist.name == new_entry["artist"])) \
                            .join(Album, and_(Album.genre_abbr == Song.genre_abbr, 
                                Album.artist_num == Song.artist_num, 
                                Album.letter == Song.album_letter, 
                                Album.name == new_entry["album"])) \
                            .filter(Song.name == new_entry["song"]).one()
            old_times_played = song_entry.times_played

            song_entry.last_played = datetime.now()
            session.commit()
            song_entry.times_played = old_times_played + 1
            session.commit()

            reference_type = REFERENCE_TYPE.IN_KLAP4
            reference = song_entry.genre_abbr + str(song_entry.artist_num) + song_entry.album_letter
        except:
            reference_type = REFERENCE_TYPE.MANUAL
            reference = str(new_entry)
        
        session.query(PlaylistEntry) \
            .filter(
                and_(PlaylistEntry.dj_id == dj_id, PlaylistEntry.playlist_name == p_name,
                     PlaylistEntry.index == index,
                     PlaylistEntry.entry == entry)
            ) \
            .update({PlaylistEntry.entry: new_entry,
                     PlaylistEntry.reference: reference,
                     PlaylistEntry.reference_type: reference_type},
                     synchronize_session=False)
        session.commit()
    
    elif new_index is not None and entry is None and new_entry is None:
        old_index = index
        playlist_entries = session.query(PlaylistEntry) \
            .filter(
                and_(PlaylistEntry.dj_id == dj_id, PlaylistEntry.playlist_name == p_name) \
            ) \
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
            # Move the item currently in the new spot out of bounds
            playlist_entries[new_index-1].index = -1

            # Move the item that needs to be in the new spot into the new spot
            playlist_entries[old_index-1].index = new_index
            session.commit()
            # For everything between the spot after the new spot and the old spot, increase the index
            for entry in playlist_entries[new_index:(old_index-1)]:
                entry.index = entry.index + 1
            
            session.commit()
            # Move the out of bounds item next to the new spot
            playlist_entries[new_index-1].index = new_index + 1
            session.commit()
        
        else:
            pass

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
