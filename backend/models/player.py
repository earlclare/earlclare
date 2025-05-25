# backend/models/player.py
from backend.app import db # Import db from app.py

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    is_pro_player = db.Column(db.Boolean, default=False, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)

    def __repr__(self):
        return f'<Player {self.name}>'
