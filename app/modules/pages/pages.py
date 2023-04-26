from flask import Blueprint, render_template, abort
from flask.views import MethodView
from jinja2 import TemplateNotFound
from models import Currency, AccountGroup, BaseModel
import models

pages_bp = Blueprint(
        name='pages',
        import_name=__name__,
        url_prefix='/pages',
        template_folder='pages_templates'
    )


class TableView(MethodView):
    
    def get(self, model: BaseModel):
        if model is None:
            abort(404)
           
        model = models.__dict__[model] 
        items = model.query.all()

        try:
            return render_template(
                'table_items.html',
                items=items,
                title=model.__name__
            )
        except TemplateNotFound:
            print(f"TemplateNotFound: {model.__name__}")
            abort(404)

pages_bp.add_url_rule(rule='/<model>/', view_func=TableView.as_view('table_view'))