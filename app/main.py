
from models import db
from app_build import app

from routes.index import *
from routes.currency import *
from routes.account_group import *
from routes.account_type import *
from routes.account import *
from routes.account_overdraft import *
from routes.transactions import *

# from modules.pages.pages import pages_bp
# app.register_blueprint(pages_bp)

# from modules.api.api import api_bp
# app.register_blueprint(api_bp)

if __name__ == '__main__':
    db.init_app(app)

    with app.app_context():
        db.create_all()
        
    app.run()
