from collections import namedtuple
import re
from typing import Union

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import and_

# Base SQLAlchemy ORM class.
SQLBase = declarative_base()
KLAP4_TAG = namedtuple("KLAP4_TAG", ["genre_abbr",
                                     "artist_num",
                                     "album_letter",
                                     "song_num",
                                     "album_review_dj_id"],
                       defaults=[None] * 4)


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

    matched = re.findall(r"([a-zA-Z]+)(\d+)?([a-zA-Z]+)?(\-?\d+)?", tag, re.IGNORECASE)[0]
    matched = [match if len(match) > 0 else None for match in matched]

    is_review = False
    try:
        matched[1] = int(matched[1])
        if matched[3][0] == '-':
            matched[3] = matched[3][1:]
            is_review = True
        matched[3] = int(matched[3])
    except (TypeError, ValueError):
        pass

    if is_review:
        matched.append(matched[3])
        matched[3] = None

    return KLAP4_TAG(*matched)


# Need to append new modules as we add them in this file.
from klap4.db_entities.software_log import *
from klap4.db_entities.artist import *
from klap4.db_entities.genre import *
from klap4.db_entities.album import *
from klap4.db_entities.song import *
from klap4.db_entities.label_and_promoter import *


def get_entity_from_tag(tag: Union[str, KLAP4_TAG]) -> SQLBase:
    if not isinstance(tag, KLAP4_TAG):
        tag = decompose_tag(tag)

    entity = None

    if tag.genre_abbr is not None:
        from klap4.db import Session
        session = Session()

        entity = session.query(Genre).filter(Genre.abbreviation == tag.genre_abbr).all()

        if tag.artist_num is not None and entity is not None:
            entity = session.query(Artist) \
                .filter(
                    and_(
                        Artist.genre_abbr == tag.genre_abbr,
                        Artist.number == tag.artist_num
                    )
                ) \
                .all()

            if entity is not None and tag.album_letter is not None:
                entity = session.query(Album) \
                    .filter(
                        and_(
                            Album.genre_abbr == tag.genre_abbr,
                            Album.artist_num == tag.artist_num,
                            Album.letter == tag.album_letter
                        )
                    ) \
                    .all()
                print(f"got {entity}")
                entity = entity[0]

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
                        .first()
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
                        .first()

    return entity
