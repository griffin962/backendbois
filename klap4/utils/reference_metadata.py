#!/usr/bin/env python3

from base64 import b64encode
from json import dumps, loads

import requests

from klap4.utils.json_utils import json


class REFERENCE_TYPE:
    MANUAL = 0
    IN_KLAP4 = 1
    SPOTIFY = 2


spotify_session = requests.Session()


def authorize_spotify():
    """Spotify only authorizes tokens 3 minutes at a time, so we must refresh it all the time."""
    global spotify_session

    SPOTIFY_ID = "c0c7c51ed9fe407696fd32dfe3e0d89c"
    SPOTIFY_SECRET = "3596e7c3022544e9865d6020e724b92d"

    auth_token = b64encode(f"{SPOTIFY_ID}:{SPOTIFY_SECRET}".encode()).decode()

    r = requests.post(url="https://accounts.spotify.com/api/token",
                      data={"grant_type": "client_credentials"},
                      headers={"Authorization": f"Basic {auth_token}"})
    if r.status_code != 200:
        raise RuntimeError(f"Unable to authorize spotify (code: {r.status_code}): {r.json()}")

    spotify_session.headers["Authorization"] = f"Bearer {r.json()['access_token']}"


def get_manual_metadata(metadata: str) -> json:
    return loads(metadata)


def get_klap4_metadata(song_key: str) -> json:
    from klap4.db_entities import get_entity_from_tag

    song = get_entity_from_tag(song_key)

    return {
        "artist": song.artist.name,
        "album": song.album.name,
        "song": song.name
    }


def get_spotify_metadata(metadata_id: str) -> json:
    r = spotify_session.get(f"https://api.spotify.com/v1/tracks/{metadata_id}")

    # Spotify only authorizes tokens 3 minutes at a time so we have to retry from time to time.
    if r.status_code == 401:
        authorize_spotify()
        r = spotify_session.get(f"https://api.spotify.com/v1/tracks/{metadata_id}")

    if r.status_code != 200:
        raise RuntimeError(f"Error to contacting spotify (status code = {r.status_code}): {r.json()}")

    song_data = r.json()

    try:
        return_data = {
            "artist": song_data["artists"][0]["name"],
            "album": song_data["album"]["name"],
            "song": song_data["name"]
        }
    except KeyError as e:
        raise RuntimeError("Error processing spotify track metadata.") from e

    return return_data


normalize_metadata = {
    REFERENCE_TYPE.MANUAL: lambda metadata : dumps({key.lower(): value for key, value in loads(metadata).items()}),
    REFERENCE_TYPE.IN_KLAP4: lambda song_key: song_key,
    REFERENCE_TYPE.SPOTIFY: lambda song_id: song_id,
}


get_metadata = {
    REFERENCE_TYPE.MANUAL: get_manual_metadata,
    REFERENCE_TYPE.IN_KLAP4: get_klap4_metadata,
    REFERENCE_TYPE.SPOTIFY: get_spotify_metadata,
}


