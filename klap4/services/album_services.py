from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

from klap4.db_entities import SQLBase, decompose_tag, get_entity_from_tag
from klap4.db_entities.genre import Genre
from klap4.db_entities.artist import Artist
from klap4.db_entities.album import Album, AlbumReview, AlbumProblem
from klap4.db_entities.song import Song
from klap4.utils import get_json, format_object_list


def list_new_albums() -> list:
    from datetime import datetime, timedelta

    from klap4.db import Session
    session = Session()

    new_album_limit = datetime.now() - timedelta(days=30*6)

    album_list = session.query(Album) \
        .filter(Album.date_added > new_album_limit).all()

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


def list_reviews(album_id: str) -> list:
    from klap4.db import Session
    session = Session()

    new_id = decompose_tag(album_id)
    
    reviews = session.query(AlbumReview) \
        .filter(and_(AlbumReview.genre_abbr == new_id[0], AlbumReview.artist_num == new_id[1], AlbumReview.album_letter == new_id[2])).all()
    
    return format_object_list(reviews)


def list_problems(album_id: str) -> list:
    from klap4.db import Session
    session = Session()

    new_id = decompose_tag(album_id)

    problems = session.query(AlbumProblem) \
        .filter(and_(AlbumProblem.genre_abbr == new_id[0], AlbumProblem.artist_num == new_id[1], AlbumProblem.album_letter == new_id[2])).all()

    return format_object_list(problems) 


def list_songs(album_id: str) -> list:
    from klap4.db import Session
    session = Session()

    new_id = decompose_tag(album_id)

    songs = session.query(Song) \
        .filter(and_(Song.genre_abbr == new_id[0], Song.artist_num == new_id[1], Song.album_letter == new_id[2])).all()

    return format_object_list(songs)


def display_album(album_id: str):
    from klap4.db import Session
    session = Session()

    info_list = []

    new_id = decompose_tag(album_id)
    
    reviews = list_reviews(album_id)
    info_list.append(reviews)
    problems = list_problems(album_id)
    info_list.append(problems)
    songs = list_songs(album_id)
    info_list.append(songs)

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


def generate_chart(format: str, weeks: int) -> list:
    from datetime import datetime, timedelta

    from klap4.db import Session
    session = Session()

    chart_list = None

    weeks_ago = datetime.now() - timedelta(weeks=int(weeks))
    new_album_limit = datetime.now() - timedelta(days=30*6)

    if format == "all":
        chart_list = session.query(Song.genre_abbr, Song.artist_num, Song.album_letter, func.sum(Song.times_played)) \
            .filter(Song.last_played > weeks_ago
            ) \
            .group_by(Song.genre_abbr, Song.artist_num, Song.album_letter) \
            .all()
        
    elif format == "new":
        chart_list = session.query(Song.genre_abbr, Song.artist_num, Song.album_letter, func.sum(Song.times_played)) \
            .join(Album, and_(Album.date_added > new_album_limit, Song.genre_abbr == Album.genre_abbr, Song.artist_num == Album.artist_num)) \
            .filter(Song.last_played > weeks_ago) \
            .group_by(Song.genre_abbr, Song.artist_num, Song.album_letter) \
            .all()
    
    sorted_charts = sorted(chart_list, key=lambda x:(-x[3], x[0], x[1], x[2]))
    return sorted_charts


def charts_format(chart_list):
    formatted_list = []
    for entry in chart_list:
        genre_tag = entry[0]
        artist_tag = genre_tag + str(entry[1])
        album_tag = artist_tag + entry[2]

        genre = get_entity_from_tag(genre_tag)
        artist = get_entity_from_tag(artist_tag)
        album = get_entity_from_tag(album_tag)

        formatted_album = {
                    "album_id": album_tag,
                    "rank": chart_list.index(entry)+1,
                    "genre": genre.name,
                    "artist_name": artist.name,
                    "album_name": album.name,
                    "label_name": None if album.label_id is None else album.label.name,
                    "promoter_name": None if album.promoter_id is None else album.promoter.name,
                    "times_played": entry[3]
        }
        formatted_list.append(formatted_album)
    
    return formatted_list
    
