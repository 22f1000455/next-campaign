from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)
    ad_requests = db.relationship('AdRequest', backref='influencer', lazy=True, foreign_keys='AdRequest.influencer_id')
    
    influencer_profile = db.relationship('InfluencerProfile', backref='user_profile', overlaps="influencer_profile_data,user", uselist=False)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    goals = db.Column(db.Text, nullable=False)
    visibility = db.Column(db.String(50), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class InfluencerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    niche = db.Column(db.String(150), nullable=True)
    reach = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('influencer_profile_data', overlaps="influencer_profile,user_profile"))