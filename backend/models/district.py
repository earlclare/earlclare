# backend/models/district.py
from backend.app import db # Import db from app.py

class District(db.Model):
    __tablename__ = 'districts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    teams = db.relationship('Team', backref='district', lazy=True)

    def __repr__(self):
        return f'<District {self.name}>'
