import flask as f
from flask import jsonify
from flask_login import login_required, current_user
from ..util import *
import TruckAPI as t

admin_bp = f.Blueprint('admin', __name__)


@admin_bp.route('/main', methods=['POST', 'GET'])
@login_required
def main():
    bread_crumbs = {'Data': 'admin.main'}
    if not current_user.perms:
        return f.redirect(f.url_for('index'))
    t5 = get_top_five_cats()
    return f.render_template('pages/data.html', trucks=t5, BreadCrumbs=bread_crumbs)


@admin_bp.route('/refresh', methods=['POST', 'GET'])
@login_required
def refresh():
    if not current_user.perms:
        return f.redirect(f.url_for('index'))
    update_database()
    return f.redirect(f.url_for('admin.main'))


@admin_bp.route('/get_data', methods=['GET'])
def get_data():
    tname = f.request.args.get('Name', None)
    if not tname: return jsonify(result='')
    td = t.Trucks.query.filter_by(Name=tname).first()
    if not td: return jsonify(result='')
    data = t.GraphData.query.filter_by(Truck_ID=td.TruckID).all()
    temp = {}
    for x in data:
        date = x.Time
        date = date.strftime("%d %b %Y")
        ups = 0
        fq = 0
        if x.Ratings != 'No Ratings': ups = x.Ratings
        temp[date] = {}
        temp[date]['ups'] = ups
        if x.Freq: fq = x.Freq
        temp[date]['freq'] = fq
    return jsonify(result=temp)


@admin_bp.route('/rate', methods=['POST'])
@login_required
def rate():
    form = RatingForm(f.request.form, meta={'csrf': False})
    if form.validate_on_submit():
        truck = t.Trucks.query.filter_by(Name=form.truck.data).first()
        rating = t.Ratings(User_ID=current_user.UserID, Truck_ID=truck.TruckID, Speed=form.speed.data,
                           Value=form.Value.data, Quality=form.quality.data, Comment=form.comment.data)
        t.db.session.add(rating)
        t.db.session.commit()
    return f.redirect(f.url_for('index'))


@admin_bp.route('/manual_email', methods=['GET'])
@login_required
def manual_email():
    if not current_user.perms:
        return f.redirect(f.url_for('index'))
    email_clients()
    return f.redirect(f.url_for('admin.main'))


@admin_bp.route('/update_cache', methods=['GET'])
@login_required
def update_cache():
    if not current_user.perms:
        return f.redirect(f.url_for('index'))
    get_trucks(force=True)
    return f.redirect(f.url_for('admin.main'))
