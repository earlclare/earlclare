# backend/models/__init__.py
# This file can remain empty or explicitly import models if preferred for organization,
# but the models are already imported in app.py for db.create_all() context.
# For clarity if other modules need to import all models from this package:
from .district import District
from .team import Team
from .player import Player
from .user import User

__all__ = ['District', 'Team', 'Player', 'User']
