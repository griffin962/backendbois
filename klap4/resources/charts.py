from flask import request, jsonify
from flask_restful import Resource

from klap4.services.charts_services import generate_chart, charts_format

class ChartsAPI(Resource):
    def get(self, form, weeks):
        if weeks > 104 or weeks < 1:
            return jsonify(error="Bad request"), 400
        else:
            charts = generate_chart(form, weeks)
            charts = charts_format(charts)
            return jsonify(charts)