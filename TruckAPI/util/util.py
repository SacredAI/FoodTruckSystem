import math
import time
import datetime

import requests, json
from flask_mail import Message

import TruckAPI as t

cache = {'refresh': 0, 'trucks': {}}
nearest_half = lambda x: round(x * 2) / 2


def update_database():
    from .models import Trucks
    url = "http://www.bnefoodtrucks.com.au/api/1/trucks"

    try:
        response = requests.get(url)

        data = response.json()
        for x in data:
            truck = Trucks.query.filter_by(TruckID=x['truck_id']).first()
            if truck:
                if truck.Name != x['name']: truck.Name = x['name']
                if truck.Category != x['category']: truck.Category = x['category']
                if truck.Bio != x['bio']: truck.Bio = x['bio']
                if truck.Avatar != x['avatar']['src']: truck.Avatar = x['avatar']['src']
                if truck.Cover != x['cover_photo']['src']: truck.Cover = x['cover_photo']['src']
                if truck.Website != x['website']: truck.Website = x['website']
                if truck.Facebook != x['facebook_url']: truck.Facebook = x['facebook_url']
                if truck.Instagram != x['instagram_handle']: truck.Instagram = x['instagram_handle']
                if truck.Twitter != x['twitter_handle']: truck.Twitter = x['twitter_handle']
            else:
                avt = x['avatar']
                if len(avt) < 1:
                    continue
                e = t.Trucks(TruckID=x['truck_id'], Name=x['name'], Category=x['category'], Bio=x['bio'],
                             Avatar=avt['src'], Cover=x['cover_photo']['src'],
                             Website=x['website'], Facebook=x['facebook_url'], Instagram=x['instagram_handle'],
                             Twitter=x['twitter_handle'])
                t.db.session.add(e)
        t.db.session.commit()
    except:
        pass


def get_categories():
    '''
    :return: Dictionary containing the number of trucks in each category
    :rtype: dict
    '''
    data = t.Trucks.query.order_by(t.Trucks.Category).all()
    cat = {}
    for x in data:
        try:
            cat[x.Category] += 1
        except:
            cat[x.Category] = 1
    return cat


def get_trucks(force=False):
    '''
    :param force: Bool value to force an Update of the cache
    :return: Dict containing all trucks and set data points about said trucks
    :rtype: dict
    '''
    global cache
    if cache['refresh'] > time.time() and not force:
        return cache['trucks']
    data = t.Trucks.query.all()
    trucks = {}
    for x in data:
        trucks[x.Name] = {}
        trucks[x.Name]['Category'] = x.Category
        rating, s, q, v, users = get_rating(x.TruckID)
        if users:
            trucks[x.Name]['Ratings'] = users
        trucks[x.Name]['Rating'] = {}
        trucks[x.Name]['Rating']['Avg'] = {}
        if isinstance(rating, str):
            trucks[x.Name]['Rating']['Avg']['val'] = rating
        else:
            trucks[x.Name]['Rating']['Avg']['d'], trucks[x.Name]['Rating']['Avg']['val'] = math.modf(rating)
        trucks[x.Name]['Rating']['Speed'] = {}
        if isinstance(s, str):
            trucks[x.Name]['Rating']['Speed']['val'] = s
        else:
            trucks[x.Name]['Rating']['Speed']['d'], trucks[x.Name]['Rating']['Speed']['val'] = math.modf(s)
        trucks[x.Name]['Rating']['Quality'] = {}
        if isinstance(q, str):
            trucks[x.Name]['Rating']['Quality']['val'] = q
        else:
            trucks[x.Name]['Rating']['Quality']['d'], trucks[x.Name]['Rating']['Quality']['val'] = math.modf(q)
        trucks[x.Name]['Rating']['Value'] = {}
        if isinstance(v, str):
            trucks[x.Name]['Rating']['Value']['val'] = v
        else:
            trucks[x.Name]['Rating']['Value']['d'], trucks[x.Name]['Rating']['Value']['val'] = math.modf(v)
        trucks[x.Name]['Bio'] = x.Bio
        trucks[x.Name]['Avatar'] = x.Avatar
        trucks[x.Name]['Cover'] = x.Cover
        trucks[x.Name]['Socials'] = {}
        trucks[x.Name]['Socials']['Website'] = x.Website
        trucks[x.Name]['Socials']['Facebook'] = x.Facebook
        trucks[x.Name]['Socials']['Instagram'] = x.Instagram
        trucks[x.Name]['Socials']['Twitter'] = x.Twitter
    cache['trucks'] = trucks
    cache['refresh'] = (time.time() + 3600)
    return trucks


def percentage_rating(tid):
    '''
    :param tid: Truck ID From the database
    :return: The trucks rating as a Percentage
    :rtype: float
    '''
    data = t.Ratings.query.filter_by(Truck_ID=tid).all()
    if len(data) < 1:
        return "No Ratings"
    s, q, v = 0, 0, 0
    for x in data:
        s += x.Speed
        q += x.Quality
        v += x.Value
    avg = (s+q+v)/3
    n = len(data) * 3
    avg = round((avg/n)*100, 1)
    return avg


def get_rating(tid):
    '''
    :param tid: Truck ID from the database
    :return: Average, speed, quality and value Star ratings and a dict of all user ratings
    :rtype: float, dict
    '''
    data = t.Ratings.query.filter_by(Truck_ID=tid).all()
    if len(data) < 1:
        return "No Ratings", "No Ratings", "No Ratings", "No Ratings", False
    s, q, v = 0, 0, 0
    users = {}
    for x in data:
        u = t.Users.query.filter_by(UserID=x.User_ID).first()
        users[u.username] = {}
        users[u.username]['speed'] = x.Speed
        users[u.username]['quality'] = x.Quality
        users[u.username]['value'] = x.Value
        us, uq, uv = 0, 0, 0
        tdata = t.Ratings.query.filter_by(User_ID=x.User_ID).all()
        for trk in tdata:
            if trk.Truck_ID == x.Truck_ID: continue
            us += trk.Speed
            uq += trk.Quality
            uv += trk.Value
        n = (us + uq + uv) / 3
        if n == 0: n = 1
        n = n / len(tdata) * 3
        uav = (x.Speed + x.Quality + x.Value) / 3
        users[u.username]['avg'] = {}
        temp = round((uav / n) * 5, 1)
        temp = nearest_half(temp)
        users[u.username]['avg']['d'], users[u.username]['avg']['val'] = math.modf(temp)
        users[u.username]['comment'] = x.Comment
        s += x.Speed
        q += x.Quality
        v += x.Value
    avg = (s + q + v) / 3
    n = len(data) * 3
    avg = round((avg / n) * 5, 1)
    s = round(s / n * 5, 1)
    q = round(q / n * 5, 1)
    v = round(v / n * 5, 1)

    return nearest_half(avg), nearest_half(s), nearest_half(q), nearest_half(v), users


def sort_overall(tbl, val):
    if tbl[val]['avg'] == 'No Ratings':
        return -1
    return int(tbl[val]['avg'])


def frequency_calc(tid):
    '''
    :param tid: Truck ID from the database
    :return: Speed, Quality and Value Frequency
    :rtype: float
    '''
    data = t.Ratings.query.filter_by(Truck_ID=tid).all()
    if len(data) < 1:
        return 0, 0, 0
    s, q, v = 0, 0, 0
    for x in data:
        if x.Speed == 1: s += 1
        if x.Quality == 1: q += 1
        if x.Value == 1: v += 1
    n = len(data)
    s = s / n
    q = q / n
    v = v / n
    return s, q, v


def variance_calc(tid):
    '''
    :param tid: Truck ID from the database
    :return: Average Varience
    :rtype: float
    '''
    data = t.Ratings.query.filter_by(Truck_ID=tid).all()
    if len(data) < 1:
        return 0
    sma, smi, qma, qmi, vma, vmi = 0, 0, 0, 0, 0, 0
    for x in data:
        sma = max(sma, x.Speed)
        smi = min(smi, x.Speed)
        qma = max(qma, x.Quality)
        qmi = min(qmi, x.Quality)
        vma = max(vma, x.Value)
        vmi = min(vmi, x.Value)
    sv = sma - smi
    qv = qma - qmi
    vv = vma - vmi
    avg = (sv + qv + vv) / 3
    return avg


def get_top_five_cats():
    '''
    :return: Dict of top five categories and all food trucks contained in them
    :rtype: dict
    '''
    cat = get_categories()
    t5 = {}
    for category in cat:
        t5[category] = {}
        if cat[category] < 3: continue
        data = t.Trucks.query.filter_by(Category=category).all()
        temp = {}
        for x in data:
            temp[x.Name] = {}
            _, s, q, v, users = get_rating(x.TruckID)
            rating = percentage_rating(x.TruckID)
            leng = 0
            if users: leng = len(users)
            fs, fq, fv = frequency_calc(x.TruckID)
            fqu = ((fs + fq + fv) / 3) * 100
            var = variance_calc(x.TruckID)
            gd = t.GraphData(Truck_ID=x.TruckID, Ratings=rating,
                             Freq=fqu)  # Time=(datetime.datetime.now()-datetime.timedelta(days=1)) -- This is for adding testing data to the database
            t.db.session.add(gd)
            temp[x.Name]['avg'] = rating
            temp[x.Name]['Speed'] = fs
            temp[x.Name]['Quality'] = fq
            temp[x.Name]['Value'] = fv
            temp[x.Name]['var'] = var
            temp[x.Name]['traffic'] = leng
        t.db.session.commit()
        for k in sorted(temp, key=lambda k: sort_overall(temp, k), reverse=True):
            t5[category][k] = temp[k]
    st5 = {}
    count = 1
    for k in sorted(t5, key=lambda k: len(t5[k]), reverse=True):
        if count > 5: continue
        count += 1
        st5[k] = t5[k]
    return st5


def sort_trucks(tbl, val):
    if tbl[val] == 'No Ratings':
        return -1
    return int(tbl[val])


def get_top_five_trucks(cat):
    '''
    :param cat: Category to get the top 5 from
    :return: Dict of top 5 food trucks from a specific food truck
    :rtype: dict
    '''
    t5 = {}
    data = None
    if cat != "":
        data = t.Trucks.query.filter_by(Category=cat).all()
    else:
        data = t.Trucks.query.all()
    temp = {}
    for x in data:
        rating, s, q, v, users = get_rating(x.TruckID)
        temp[x.Name] = rating
    count = 1
    for k in sorted(temp, key=lambda k: sort_trucks(temp, k), reverse=True):
        if count > 5: continue
        count += 1
        t5[k] = temp[k]
    return t5


def email_clients():
    users = t.Users.query.filter_by(notifications=True).all()
    with t.app.app_context():
        with t.mail.connect() as conn:
            for user in users:
                msg = "Recommended Food Trucks!\n\n Heres the top 5 Trucks from your Favourite Categories!\n\n"
                prefs = t.Preferences.query.filter_by(User_ID=user.UserID).all()
                for pref in prefs:
                    trucks = get_top_five_trucks(pref.Preferencen)
                    for tr, r in trucks.items():
                        msg = msg + str(tr) + ": " + str(r) + "\n"
                msg = Message(subject="Recommended Food Trucks", body=msg, recipients=[user.email])
                conn.send(msg)
