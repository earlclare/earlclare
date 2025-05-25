# backend/app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
import click

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

def create_app():
    app = Flask(__name__)

    # Configuration for MySQL
    # IMPORTANT: Set these environment variables in your deployment environment.
    # For local development, you might set them in your .env file or directly in your shell.
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST', 'localhost') # Default to localhost
    DB_NAME = os.environ.get('DB_NAME', 'tournament_db') # Default database name

    # Check if essential DB environment variables are set
    if not DB_USER or not DB_PASSWORD:
        print("WARNING: DB_USER and DB_PASSWORD environment variables are not set. " +
              "Database connection will likely fail.")
        # You could raise an error here or use a default SQLite fallback for purely local dev
        # For this setup, we'll proceed and let it fail if not set, to emphasize requirement.
        
    # Construct the MySQL URI. PyMySQL is the driver.
    # Example: mysql+pymysql://user:password@host/dbname
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}" \
        if DB_USER and DB_PASSWORD else None # Or fallback to SQLite for local if desired

    # Fallback to SQLite if MySQL credentials are not provided (optional, for easier local dev without MySQL)
    # To make this more robust for the user's request, we will *not* fallback to SQLite here.
    # The user explicitly asked for MySQL. If credentials are not set, it should indicate an issue.
    if not app.config['SQLALCHEMY_DATABASE_URI']:
         # This path should ideally not be taken if user wants MySQL.
         # Forcing an error or clear warning is better.
         # For now, let's assume the user will set the env vars.
         # If we were to add a fallback:
         # print("INFO: MySQL credentials not fully set, attempting to fall back to SQLite for local dev.")
         # base_dir = os.path.abspath(os.path.dirname(__file__))
         # instance_path = os.path.join(base_dir, 'instance')
         # if not os.path.exists(instance_path):
         #    os.makedirs(instance_path)
         # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'tournament_fallback.db')
         pass # Let it be None if credentials aren't set, connection will fail clearly.


    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'a_very_secret_key' # Change in production
    
    # Add a comment for the user:
    # NOTE TO USER: Ensure the MySQL database (e.g., 'tournament_db') is created on your MySQL server
    # and that the user specified by DB_USER has the necessary permissions.

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app) 

    # ... (rest of the imports, db.create_all, blueprint registrations, CLI command) ...
    # Ensure these parts are still present and correct as from the previous implementation.
    from backend.models.district import District
    from backend.models.team import Team
    from backend.models.player import Player
    from backend.models.user import User

    with app.app_context():
        if app.config['SQLALCHEMY_DATABASE_URI']: # Only attempt if URI is set
            try:
                db.create_all() 
                # Pre-populate districts
                if District.query.count() == 0:
                    districts_data = [
                        "Corozal", "Orange Walk", "Belize City", 
                        "Cayo", "Stann Creek", "Toledo"
                    ]
                    for district_name in districts_data:
                        district = District(name=district_name)
                        db.session.add(district)
                    db.session.commit()
            except Exception as e:
                print(f"ERROR: Could not connect to database or create tables: {e}")
                print("Please ensure your MySQL server is running, the database exists, " +
                      "and your environment variables (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME) are correctly set.")
        else:
            print("ERROR: SQLALCHEMY_DATABASE_URI is not set. Database operations will fail.")
            print("Please set DB_USER and DB_PASSWORD environment variables for MySQL connection.")


    from backend.routes.district_routes import district_bp
    from backend.routes.team_routes import team_bp
    app.register_blueprint(district_bp, url_prefix='/api')
    app.register_blueprint(team_bp, url_prefix='/api')

    @app.cli.command("create-admin")
    @click.option('--username', required=True, help='Username for the admin user.')
    @click.option('--password', required=True, help='Password for the admin user.')
    def create_admin_command(username, password):
        with app.app_context():
            if not app.config.get('SQLALCHEMY_DATABASE_URI'):
                print("ERROR: Database URI not configured. Cannot create admin user.")
                return
            if User.query.filter_by(username=username).first():
                print(f'Error: Admin user with username {username} already exists.')
                return
            admin_user = User(username=username)
            admin_user.set_password(password)
            try:
                db.session.add(admin_user)
                db.session.commit()
                print(f'Admin user {username} created successfully.')
            except Exception as e:
                db.session.rollback()
                print(f'Error creating admin user {username}: {str(e)}')
    return app
