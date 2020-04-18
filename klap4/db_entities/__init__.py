from collections import namedtuple
import re
from typing import Union

from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_

# Base SQLAlchemy ORM class.
SQLBase = declarative_base()


KLAP4_TAG = namedtuple("KLAP4_TAG", ["genre_abbr",
                                     "artist_num",
                                     "album_letter",
                                     "song_num",
                                     "album_review_dj_id"],
                       defaults=[None] * 5)
PLAYLIST_TAG = namedtuple("PLAYLIST_TAG", ["dj_id",
                                           "name",
                                           "song_num"],
                          defaults=[None] * 3)


def decompose_tag(tag: str, *, regex_hint: Union[str, None] = None) -> Union[KLAP4_TAG, PLAYLIST_TAG]:
    """Decomposes a music id/tag into it's respective attributes.

    Examples:
        ``RR``: Genre with abbreviation "RR".
        ``RR3B5``: The fifth song in the 2nd album of the 3rd artist in the "RR" genre.
        ``RR3B-abcdef``: A review of the previously defined album by the dj with id ``abcdef``.
        ``RR3B!abcdef``: A problem report of the previously defined album by the dj with id ``abcdef``.
        ``abcdef+My Playlist``: A playlist titled ``My Playlist`` from dj ``abcdef``.
        ``abcdef+My Playlist+5``: The fifth playlist entry in the above playlist.

    Args:
        tag: The full tag string.
        regex_hint: A hint as to what the tag is, if ``None`` then try to figure it out ourselves. Searches for the
                    ``+`` within the first 7 characters for a playlist tag, else treat it as a klap4 tag. Valid values
                    are ``"klap4"``, ``"playlist"``, or ``None``

    Returns:
         A named tuple containing each of the attributes, or ``None`` if it is not found.
    """
    regexes = {
        "klap4": r"([a-z]+)(\d+)?([a-z]+)?(\d+|(\-|\!)[a-z0-9]+)?",
        "playlist": r"([a-z0-9]+)(?:\+([^\n\+\t]+)(?:\+(\d+))?)?"
    }
    if len(tag) == 0:
        raise ValueError("id must not be empty")
    elif regex_hint is None:
        if '+' in tag[:8]:
            regex_hint = "playlist"
        else:
            regex_hint = "klap4"
    elif regex_hint not in regexes:
        raise ValueError(f"Unknown regex hint '{regex_hint}'.")

    decomposed_tag = None
    regex_hint = regex_hint.lower()

    matched = re.findall(regexes[regex_hint], tag, re.IGNORECASE)[0]
    matched = [match if len(match) > 0 else None for match in matched]

    if regex_hint == "klap4":
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

        decomposed_tag = KLAP4_TAG(*matched)
    elif regex_hint == "playlist":
        try:
            matched[2] = int(matched[2])
        except (TypeError, ValueError):
            pass

        decomposed_tag = PLAYLIST_TAG(*matched)

    return decomposed_tag


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
from klap4.db_entities.dj import *
from klap4.db_entities.genre import *
from klap4.db_entities.album import *
from klap4.db_entities.song import *
from klap4.db_entities.label_and_promoter import *
from klap4.db_entities.playlist import *
from klap4.db_entities.program import *


def get_entity_from_tag(tag: Union[str, KLAP4_TAG, PLAYLIST_TAG]) -> SQLBase:
    # If tag is a string, turn it into a named tuple
    if isinstance(tag, str):
        tag = decompose_tag(tag)

    entity = None

    try:
        from klap4.db import Session
        session = Session()
        if isinstance(tag, KLAP4_TAG) and tag.genre_abbr is not None:
            entity = session.query(Genre) \
                .filter(Genre.abbreviation == tag.genre_abbr) \
                .one()

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
        elif isinstance(tag, PLAYLIST_TAG) and tag.dj_id is not None:
            entity = session.query(DJ) \
                .filter(DJ.id == tag.dj_id) \
                .one()

            if tag.name is not None:
                entity = session.query(Playlist) \
                    .filter(
                        and_(
                            Playlist.dj_id == tag.dj_id,
                            Playlist.name == tag.name
                        )
                    ) \
                    .one()

                if tag.song_num is not None:
                    entity = session.query(PlaylistEntry) \
                        .filter(
                            and_(
                                PlaylistEntry.dj_id == tag.dj_id,
                                PlaylistEntry.playlist_name == tag.name,
                                PlaylistEntry.index == tag.song_num
                            )
                        ) \
                        .one()
    except NoResultFound as e:
        tag_str = ''.join([str(d) if d is not None else '' for d in tag])
        raise NoResultFound(f"No tag found: '{tag_str}'") from e

    return entity
