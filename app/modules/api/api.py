from flask import Blueprint, jsonify
from flask.views import MethodView
import models
from models import BaseModel

api_bp = Blueprint(
        name='api',
        import_name=__name__,
        url_prefix='/api'
    )


class APIModelView(MethodView):
    def get(self, model: BaseModel):

        model = models.__dict__[model]

        items = model.query.all()

        response = [item.to_dict() for item in items]
        return jsonify(response)


api_bp.add_url_rule(rule='/<model>', view_func=APIModelView.as_view('model_view'))