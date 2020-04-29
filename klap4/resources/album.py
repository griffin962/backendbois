from flask import request, jsonify
from flask_restful import Resource

from klap4.db_entities import get_entity_from_tag
from klap4.services.album_services import new_album_list, search_albums

class AlbumListAPI(Resource):
    def get(self):
        album_list = new_album_list()
        return jsonify(album_list)
    
    def post(self):
        json_data = request.get_json(force=True)
        genre = json_data['genre']
        artist = json_data['artistName']
        name = json_data['name']
        album_list = search_albums(genre, artist, name)
        return jsonify(album_list)


class AlbumAPI(Resource):
    def get(self, ref):
        album = get_entity_from_tag(ref)
        serialized_album = album.serialize()
        return serialized_album


class AlbumReviewAPI(Resource):
    def post(self, ref):
        json_data = request.get_json(force=True)
        dj_id = json_data['dj_id']
        content = json_data['content']
        try:
            review = add_review(ref, dj_id, content)
        except:
            return jsonify(error='Bad request'), 400

        return "Added"