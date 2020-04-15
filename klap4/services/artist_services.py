from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

from klap4.db_entities import SQLBase, decompose_tag
from klap4.db_entities.genre import Genre
from klap4.db_entities.artist import Artist
from klap4.db_entities.album import Album
from klap4.utils import *


def search_artists(genre: str, name: str) -> list:
    from klap4.db import Session
    session = Session()

    artist_list = session.query(Artist) \
        .join(
            Genre, and_(Genre.name.like(genre+'%'), Genre.abbreviation == Artist.genre_abbr)
        ) \
        .filter(
            Artist.name.like(name+'%')
        ) \
        .all()
    
    return format_object_list(artist_list)


def list_albums(artist_id: str) -> SQLBase:
    entity = None

    from klap4.db import Session
    session = Session()

    new_id = decompose_tag(artist_id)

    entity = session.query(Album) \
        .filter( and_(Album.genre_abbr == new_id[0], Album.artist_num == new_id[1])
        ) \
        .all()
    
    return entity