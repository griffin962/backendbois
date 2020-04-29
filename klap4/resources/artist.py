from flask import request, jsonify
from flask_restful import Resource

from klap4.db_entities import get_entity_from_tag
from klap4.services.artist_services import new_artist_list, search_artists


class ArtistListAPI(Resource):
    def get(self):
        artist_list = new_artist_list()
        return jsonify(artist_list)
    

    def post(self):
        json_data = request.get_json(force=True)
        genre = json_data['genre']
        name = json_data['name']
        artist_list = search_artists(genre, name)
        return jsonify(artist_list)

class ArtistAPI(Resource):
    def get(self, ref):
        artist = get_entity_from_tag(ref)
        serialized_artist = artist.serialize()
        return jsonify(serialized_artist)