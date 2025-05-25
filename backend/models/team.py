# backend/models/team.py
from backend.app import db # Import db from app.py

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(150), nullable=True)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=False)
    pro_player_count = db.Column(db.Integer, default=0, nullable=False)
    
    players = db.relationship('Player', backref='team', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Team {self.name}>'
