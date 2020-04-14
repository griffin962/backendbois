from collections import namedtuple
import re
from typing import Union

from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import and_

# Base SQLAlchemy ORM class.
SQLBase = declarative_base()


def get_json(sql_object: SQLBase) -> dict:
    dict_data = vars(sql_object).copy()
    dict_data.pop("_sa_instance_state")
    dict_data["id"] = sql_object.id
    return dict_data


# class JSONable:
#     def __json__(self):
#         raise NotImplementedError(f"Class {type(self).__name__} does not implement the .json() interface.")
#
#     def json(self):
#         return self.__json__()


KLAP4_TAG = namedtuple("KLAP4_TAG", ["genre_abbr",
                                     "artist_num",
                                     "album_letter",
                                     "song_num",
                                     "album_review_dj_id"],
                       defaults=[None] * 5)


def decompose_tag(tag: str) -> KLAP4_TAG:
    """Decomposes a music id/tag into it's respective attributes.

    A music tag always starts out with a combination of letters, for the genre.

    Following the genre is a positive integer, for the artist.

    Third is an album letter(s?)

    Lastly is another positive integer for the song number within the album, or a negative integer
    for an album review where the negative number is a negated dj id.

    Examples:
        ``RR``: Genre with abbreviation "RK".
        ``RR3``: The third artist in the previously defined genre.
        ``RR3B``: The second album from the previously defined artist.
        ``RR3B5``: The fifth song in the previously defined album.
        ``RR3B-5``: A review of the previously defined album by the dj with id ``5``.

    Args:
        tag: The full tag string.

    Returns:
         A named tuple containing each of the attributes, or ``None`` if it is not found.
    """
    if len(tag) == 0:
        raise ValueError("id must not be empty")

    matched = re.findall(r"([a-zA-Z]+)(\d+)?([a-zA-Z]+)?(\d+|\-[a-zA-Z0-9]+)?", tag, re.IGNORECASE)[0]
    matched = [match if len(match) > 0 else None for match in matched]

    is_review = False
    try:
        matched[1] = int(matched[1])
        if matched[3][0] == '-':
            matched[3] = matched[3][1:]
            matched.append(matched[3])
            matched[3] = None
        else:
            matched[3] = int(matched[3])
    except (TypeError, ValueError):
        pass

    return KLAP4_TAG(*matched)


def full_module_name(name: str, *, module_name: str = "") -> str:
    """Expands an SQLAlchemy ORM mapped class to it's full module name

    Examples:
        ``full_module_name("Artist") == "klap4.db_entities.artist.Artist"``
        ``full_module_name("AlbumReview", module_name="Album") == "klap4.db_entities.album.AlbumReview"``

    """
    template = "klap4.db_entities"
    if module_name == "":
        module_name = name.lower()
    return f"{template}.{module_name}.{name}"


# Need to append new modules as we add them in this file.
from klap4.db_entities.software_log import *
from klap4.db_entities.artist import *
from klap4.db_entities.genre import *
from klap4.db_entities.album import *
from klap4.db_entities.song import *
from klap4.db_entities.label_and_promoter import *
#from klap4.db_entities.playlist import *
#from klap4.db_entities.user import *

def get_entity_from_tag(tag: Union[str, KLAP4_TAG]) -> SQLBase:

    # If tag is a string, turn it into a KLAP4_TAG
    if not isinstance(tag, KLAP4_TAG):
        tag = decompose_tag(tag)

    entity = None

    if tag.genre_abbr is not None:
        from klap4.db import Session
        session = Session()

        entity = session.query(Genre).filter(Genre.abbreviation == tag.genre_abbr).one()

        if tag.artist_num is not None and entity is not None:
            entity = session.query(Artist) \
                .filter(
                    and_(
                        Artist.genre_abbr == tag.genre_abbr,
                        Artist.number == tag.artist_num
                    )
                ) \
                .one()

            if entity is not None and tag.album_letter is not None:
                entity = session.query(Album) \
                    .filter(
                        and_(
                            Album.genre_abbr == tag.genre_abbr,
                            Album.artist_num == tag.artist_num,
                            Album.letter == tag.album_letter
                        )
                    ) \
                    .one()

                if entity is not None and tag.song_num is not None:
                    entity = session.query(Song) \
                        .filter(
                            and_(
                                Song.genre_abbr == tag.genre_abbr,
                                Song.artist_num == tag.artist_num,
                                Song.album_letter == tag.album_letter,
                                Song.number == tag.song_num
                            )
                        ) \
                        .one()
                elif entity is not None and tag.album_review_dj_id is not None:
                    entity = session.query(AlbumReview) \
                        .filter(
                            and_(
                                AlbumReview.genre_abbr == tag.genre_abbr,
                                AlbumReview.artist_num == tag.artist_num,
                                AlbumReview.album_letter == tag.album_letter,
                                AlbumReview.dj_id == tag.album_review_dj_id
                            )
                        ) \
                        .one()

    return entity


def search_artists(genre: str, name: str) -> SQLBase:
    entity = None

    from klap4.db import Session
    session = Session()

    entity = session.query(Artist) \
        .join(
            Genre, and_(Genre.name.like(genre+'%'), Genre.abbreviation == Artist.genre_abbr)
        ) \
        .filter(
            Artist.name.like(name+'%')
        ) \
        .all()
    
    return entity

def search_albums(genre: str, artist_name: str, name: str) -> SQLBase:
    entity = None

    from klap4.db import Session
    session = Session()

    entity = session.query(Album) \
        .join(
            Genre, and_(Genre.name.like(genre+'%'), Genre.abbreviation == Album.genre_abbr)
        ) \
        .join(Artist, and_(Artist.name.like(artist_name+'%'), Artist.number == Album.artist_num)
        ) \
        .filter(
            Album.name.like(name+'%'),
        ) \
        .all()
    
    return entity

def create_artist(genre_abbr, name):
    entity = None

    from klap4.db import Session
    session = Session()

    # Get the max number for artists in this genre category, then add 1 to it for the new artist
    entity = session.query(Artist, func.max(Artist.number)).one()
    next_num = entity.number + 1

    # Create a new artist object for the table, insert it and commit
    new_artist = Artist(genre_abbr=genre_abbr, 
                        number=int(next_num), 
                        name=name)

    session.add(new_artist)
    session.commit()

    return new_artist


def create_album(genre_abbr, artist_num, format_bitfield, label_id, promoter_id, name):
    entity = None

    from datetime import date
    from klap4.db import Session
    session = Session()

    # Get the next letter for this artist
    entity = session.query(Artist) \
        .filter(
            and_(Artist.genre_abbr == genre_abbr, Artist.number == artist_num)
        ) \
        .one()
    
    next_letter = entity.next_album_letter()

    new_album = Album(genre_abbr=genre_abbr, 
                        artist_num=int(artist_num), 
                        letter=next_letter, 
                        name=name, 
                        date_added=date.today(), 
                        missing=False, 
                        format_bitfield=format_bitfield, 
                        label_id=label_id, 
                        promoter_id=promoter_id)
    
    session.add(new_album)
    session.commit()

    return new_album

def delete_artist(artist):
    genre_abbr = artist.genre_abbr
    number = artist.number

    from klap4.db import Session
    session = Session()

    session.query(Artist).filter(and_(Artist.genre_abbr == genre_abbr, Artist.number == number)).delete()

    return

def delete_album(album):
    genre_abbr = album.genre_abbr
    artist_num = album.artist_num
    letter = album.letter

    from klap4.db import Session
    session = Session()

    session.query(Album).filter(and_(Album.genre_abbr == genre_abbr, Album.artist_num == artist_num, Album.letter == letter)).delete()

    return
