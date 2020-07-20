from flask_login import UserMixin

from TruckAPI import db
import datetime


class Users(UserMixin, db.Model):
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    AlternateID = db.Column(db.Unicode(255), unique=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(120), unique=True)
    notifications = db.Column(db.Boolean())
    perms = db.Column(db.Boolean())
    trucks = db.relationship('Trucks', backref="users", lazy=True)
    ratings = db.relationship('Ratings', backref="users", lazy=True)

    def __repr__(self):
        return '<UserName {}>'.format(self.username)

    def get_id(self):
        return self.AlternateID


class Trucks(db.Model):
    TruckID = db.Column(db.Integer, primary_key=True)
    User_ID = db.Column(db.Integer, db.ForeignKey('users.UserID'))

    Name = db.Column(db.String(255), unique=True)
    Category = db.Column(db.String(255))
    Bio = db.Column(db.String(255))
    Avatar = db.Column(db.String(255))
    Cover = db.Column(db.String(255))
    Website = db.Column(db.String(255))
    Facebook = db.Column(db.String(255))
    Instagram = db.Column(db.String(255))
    Twitter = db.Column(db.String(255))
    ratings = db.relationship('Ratings', backref="trucks", lazy=True)
    GraphData = db.relationship('GraphData', backref="trucks", lazy=True)


class Ratings(db.Model):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    User_ID = db.Column(db.Integer, db.ForeignKey('users.UserID'))
    Truck_ID = db.Column(db.Integer, db.ForeignKey('trucks.TruckID'))
    Speed = db.Column(db.Integer)
    Quality = db.Column(db.Integer)
    Value = db.Column(db.Integer)
    Comment = db.Column(db.String(255))


class Preferences(db.Model):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    User_ID = db.Column(db.Integer, db.ForeignKey('users.UserID'))
    Preferencen = db.Column(db.String(255))
    Preferenceb = db.Column(db.Boolean)


class GraphData(db.Model):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Truck_ID = db.Column(db.Integer, db.ForeignKey('trucks.TruckID'))
    Time = db.Column(db.DateTime, default=datetime.datetime.now())
    Ratings = db.Column(db.Integer)
    Freq = db.Column(db.Integer)
