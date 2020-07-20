import os
import random

import flask as f
from flask_login import LoginManager, current_user
from flask_mail import Mail, email_dispatched
from flask_wtf import CSRFProtect
from passlib.handlers.sha2_crypt import sha256_crypt

from .util import *
from .user import user_bp
from .admin import admin_bp
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api

app = f.Flask(__name__)
app.config.from_object('config')
app.secret_key = app.config["SECRET_KEY"]

mail = Mail(app)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'user.login'

login_manager.init_app(app)

# csrf = CSRFProtect(app)

app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')

api = Api(app)

db = SQLAlchemy(app)
from .util.models import Users, Trucks, Ratings, Preferences, GraphData

db.create_all()

admin = Users.query.filter_by(username='admin').first()  # Checks if the admin account exists creates one if it
# doesn't.
if admin is None:
    e = Users(username="admin", password=sha256_crypt.hash("password"),
              email="admin@example.com", notifications=False, perms=True)
    db.session.add(e)
    db.session.commit()

update_database()
email_clients()


@app.route('/', methods=['GET', 'POST'])
def index():
    trucks = get_trucks()
    form = RatingForm(meta={'csrf': False})
    return f.render_template("pages/index.html", Trucks=trucks, form=form)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(AlternateID=user_id).first()


@app.before_request
def before_request():
    f.g.user = current_user


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


# adds a timestamp to then end of a url to prevent caching
def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return f.url_for(endpoint, **values)


@app.errorhandler(404)
def page_not_found(error):
    return f.render_template("codes/404.html"), 404


def log_message(message, app):
    print(message.recipients, message.subject, message.body)


email_dispatched.connect(log_message)
