import string
import random

import flask as f
from wtforms import BooleanField, validators

from ..util import RegisterForm, LoginForm, SettingsForm, get_categories
from passlib.hash import sha256_crypt
from flask_login import login_required, login_user, logout_user, current_user
import TruckAPI as t

user_bp = f.Blueprint('user', __name__)


def id_generator(size=4, chars=string.ascii_uppercase + string.digits, oid=''):
    if oid != '':
        return oid
    oid = oid.join(random.choice(chars) for _ in range(size))
    da = t.Users.query.filter_by(AlternateID=oid).first()
    if da: return id_generator(size, chars)
    return oid


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    bread_crumbs = {'Login': 'user.login'}
    form = LoginForm(f.request.form, meta={'csrf': False})
    if form.validate_on_submit():
        user = t.Users.query.filter_by(email=form.email.data).first()
        if user is not None:
            if not user.AlternateID:
                user.AlternateID = id_generator().encode(encoding="utf-8", errors="replace")
                t.db.session.commit()
            login_user(user, remember=form.remember_me.data)
            redirect_url = f.request.args.get('next') or f.url_for('index')
            return f.redirect(redirect_url)
    return f.render_template("pages/auth.html", register=False, form=form, BreadCrumbs=bread_crumbs)


@user_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return f.redirect(f.url_for('index'))


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    bread_crumbs = {'Register': 'user.register'}
    form = RegisterForm(f.request.form, meta={'csrf': False})
    if form.validate_on_submit():
        new_user = t.Users(email=form.email.data,
                           username=form.username.data,
                           password=sha256_crypt.encrypt(form.password.data),
                           notifications=form.recommendations.data,
                           perms=False, AlternateID=id_generator().encode(encoding="utf-8", errors="replace"))
        t.db.session.add(new_user)
        cats = get_categories()
        for cat, _ in cats.items():
            preference = t.Preferences(User_ID=new_user.UserID, Preferencen=cat, Preferenceb=True)
            t.db.session.add(preference)
        t.db.session.commit()
        return f.redirect(f.url_for('user.login'))
    return f.render_template("pages/auth.html", register=True, form=form, BreadCrumbs=bread_crumbs)


@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    bread_crumbs = {'Settings': 'user.settings'}
    cats = get_categories()
    for cat, _ in cats.items():
        if cat == "": continue
        setattr(SettingsForm, cat, BooleanField(cat, [validators.Optional()]))
    form = SettingsForm(f.request.form, meta={'csrf': False})
    if form.validate_on_submit():
        if form.password.data:
            current_user.password = sha256_crypt.encrypt(form.password.data)
        if form.username.data:
            current_user.username = form.username.data
        if form.email.data:
            current_user.email = form.username.email
        if form.recommendations.data:
            current_user.notifications = form.recommendations.data
        for cat, _ in cats.items():
            if cat == "": continue
            if form[cat].data:
                p = t.Preferences.query.filter_by(User_ID=current_user.UserID, Preferencen=cat).first()
                if not p:
                    p = t.Preferences(User_ID=current_user.UserID, Preferencen=cat, Preferenceb=form[cat].data)
                else:
                    p.Preferenceb = form[cat].data
                t.db.session.add(p)
        t.db.session.commit()
        return f.redirect(f.url_for('user.settings'))
    return f.render_template("pages/settings.html", form=form, BreadCrumbs=bread_crumbs, cats=cats)
