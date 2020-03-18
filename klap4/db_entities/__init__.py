from collections import namedtuple
import re

from sqlalchemy.ext.declarative import declarative_base

# Base SQLAlchemy ORM class.
SQLBase = declarative_base()
KLAP4_TAG = namedtuple("KLAP4_TAG", ["genre_abbr", "artist_num", "album_letter", "album_review_dj_id"],
                       defaults=[None] * 4)


def decompose_tag(tag: str) -> KLAP4_TAG:
    """Decomposes a music id/tag into it's respective attributes.

    Args:
        tag: The full tag string.

    Returns:
         A named tuple containing each of the attributes, or ``None`` if it is not found.
    """
    if len(tag) == 0:
        raise ValueError("id must not be empty")

    matched = re.findall(r"([a-zA-Z]+)(\d+)?([a-zA-Z]+)?(\d+)?", tag, re.IGNORECASE)[0]
    matched = [match if len(match) > 0 else None for match in matched]

    try:
        matched[1] = int(matched[1])
        matched[3] = int(matched[3])
    except (TypeError, ValueError):
        pass

    return KLAP4_TAG(*matched)


# Need to append new modules as we add them in this file.
from klap4.db_entities.software_log import *
from klap4.db_entities.artist import *
from klap4.db_entities.genre import *
from klap4.db_entities.album import *
from klap4.db_entities.label_and_promoter import *
