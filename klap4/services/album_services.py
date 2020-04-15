from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

from klap4.db_entities import SQLBase, decompose_tag
from klap4.db_entities.genre import Genre
from klap4.db_entities.artist import Artist
from klap4.db_entities.album import Album, AlbumReview, AlbumProblem
from klap4.db_entities.song import Song
from klap4.utils import get_json, format_object_list


def list_new_albums() -> list:
    from datetime import datetime, timedelta

    from klap4.db import Session
    session = Session()

    album_list = session.query(Album) \
        .filter(datetime.now() - Album.date_added < timedelta(days=30 * 6)).all()

    return format_object_list(album_list)


def search_albums(genre: str, artist_name: str, name: str) -> list:
    from klap4.db import Session
    session = Session()

    album_list = session.query(Album) \
        .join(
            Genre, and_(Genre.name.like(genre+'%'), Genre.abbreviation == Album.genre_abbr)
        ) \
        .join(Artist, and_(Artist.name.like(artist_name+'%'), Artist.number == Album.artist_num)
        ) \
        .filter(
            Album.name.like(name+'%'),
        ) \
        .all()

    return format_object_list(album_list)
    

def display_album(album_id: str) -> list:
    from klap4.db import Session
    session = Session()

    info_list = []

    new_id = decompose_tag(album_id)

    artist = session.query(Artist) \
        .filter(and_(Artist.genre_abbr == new_id[0], Artist.number == new_id[1])).one()

    reviews = session.query(AlbumReview) \
        .filter(and_(AlbumReview.genre_abbr == new_id[0], AlbumReview.artist_num == new_id[1], AlbumReview.album_letter == new_id[2])).all()
    info_list.append(reviews)

    problems = session.query(AlbumProblem) \
        .filter(and_(AlbumProblem.genre_abbr == new_id[0], AlbumProblem.artist_num == new_id[1], AlbumProblem.album_letter == new_id[2])).all()
    info_list.append(problems)

    songs = session.query(Song) \
        .filter(and_(Song.genre_abbr == new_id[0], Song.artist_num == new_id[1], Song.album_letter == new_id[2])).all()
    info_list.append(songs)

    for sublist in info_list:
        format_object_list(sublist)
    
    info_list.append(get_json(artist))

    return info_list


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


def generate_chart(weeks: int, format: str) -> list:
    from datetime import datetime, timedelta

    from klap4.db import Session
    session = Session()

    # Need to make a flag for weeks and format
    # If format == "all", order the song list by most recently played and most plays for the last number of weeks
    # If format == "new", order the song list by most recently added, most recently played, and most plays for the last number of weeks
    chart_list = session.query(Album) \
        .filter(
            and_(datetime.now() - Album.date_added < timedelta(days=30 * 6) )
        ) \
        .all()


    return