from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

from klap4.db_entities import SQLBase, decompose_tag
from klap4.db_entities.genre import Genre
from klap4.db_entities.artist import Artist
from klap4.db_entities.album import Album
from klap4.utils import *


def new_artist_list():
    from klap4.db import Session
    session = Session()

    from datetime import datetime, timedelta
    new_album_limit = datetime.now() - timedelta(days=30*6)

    new_artist_list = session.query(Artist) \
        .join(
            Album, and_(Album.artist_id == Artist.id, Album.date_added > new_album_limit)
        ) \
        .all()

    serialized_list = []
    for artist in new_artist_list:
        serialized_artist = {
                                "id": artist.ref,
                                "name": artist.name,
                                "genre": artist.genre.name
                            }
        serialized_list.append(serialized_artist)
    
    return serialized_list
            


def search_artists(genre: str, name: str) -> list:
    from klap4.db import Session
    session = Session()

    artist_list = session.query(Artist) \
        .join(
            Genre, and_(Genre.id == Artist.genre_id, Genre.name.like(genre+'%'))
        ) \
        .filter(
            Artist.name.like(name+'%')
        ) \
        .all()
    
    serialized_list = []
    for artist in artist_list:
        serialized_artist = {
                                "id": artist.ref,
                                "name": artist.name,
                                "genre": artist.genre.name
                            }
        serialized_list.append(serialized_artist)
    
    return serialized_list