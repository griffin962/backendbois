from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

from klap4.db_entities import SQLBase, decompose_tag, get_entity_from_tag
from klap4.db_entities.genre import Genre
from klap4.db_entities.artist import Artist
from klap4.db_entities.album import Album, AlbumReview, AlbumProblem
from klap4.db_entities.song import Song
from klap4.utils import get_json, format_object_list


def new_album_list() -> list:
    from datetime import datetime, timedelta

    from klap4.db import Session
    session = Session()

    new_album_limit = datetime.now() - timedelta(days=30*6)

    new_album_list = session.query(Album) \
        .filter(Album.date_added > new_album_limit).all()
    
    serialized_list = []
    for album in new_album_list:
        serialized_album = {
                            "id": album.ref,
                            "name": album.name,
                            "artist_ref": album.artist.ref,
                            "artist": album.artist.name,
                            "genre": album.artist.genre.name,
                            "format": album.format_bitfield,
                            "missing": album.missing,
                            "new_album": album.is_new,
                            }
        serialized_list.append(serialized_album)

    return serialized_list


def search_albums(genre: str, artist_name: str, name: str) -> list:
    from klap4.db import Session
    session = Session()

    album_list = session.query(Album) \
        .join(Artist, and_(Artist.id == Album.artist_id, Artist.name.like(artist_name+'%'))
        ) \
        .join(
            Genre, and_(Genre.id == Artist.genre_id, Genre.name.like(genre+'%'))
        ) \
        .filter(
            Album.name.like(name+'%'),
        ) \
        .all()

    serialized_list = []
    for album in album_list:
        serialized_album = {
                            "id": album.ref,
                            "name": album.name,
                            "artist_ref": album.artist.ref,
                            "artist": album.artist.name,
                            "genre": album.artist.genre.name,
                            "format": album.format_bitfield,
                            "missing": album.missing,
                            "new_album": album.is_new,
                            }
        serialized_list.append(serialized_album)

    return serialized_list


def add_review(album_id: str, dj_id: str, content: str) ->SQLBase:
    from datetime import datetime
    from klap4.db import Session
    session = Session()

    new_id = decompose_tag(album_id)

    newReview = AlbumReview(genre_abbr=new_id[0],
                                artist_num=new_id[1],
                                album_letter=new_id[2],
                                dj_id=dj_id,
                                date_entered=datetime.now(),
                                content=content)
    
    session.add(newReview)
    session.commit()

    return newReview


def report_problem(album_id: str, dj_id: str, content: str) ->SQLBase:
    from klap4.db import Session
    session = Session()

    new_id = decompose_tag(album_id)

    newProblem = AlbumProblem(genre_abbr=new_id[0],
                                artist_num=new_id[1],
                                album_letter=new_id[2],
                                dj_id=dj_id,
                                content=content)
    
    session.add(newProblem)
    session.commit()

    return newProblem
    
