# backend/routes/team_routes.py
from flask import Blueprint, request, jsonify
from backend.models import db, Team, Player, District # Assuming models make these available
# db might need to be imported from backend.app depending on setup
# from backend.app import db # If db is initialized in app.py directly

team_bp = Blueprint('team_bp', __name__)

@team_bp.route('/teams', methods=['GET'])
def get_teams():
    try:
        query = Team.query
        district_id_filter = request.args.get('district_id')

        if district_id_filter:
            try:
                district_id = int(district_id_filter)
                query = query.filter(Team.district_id == district_id)
            except ValueError:
                return jsonify({'error': 'Invalid district_id format. Must be an integer.'}), 400
        
        teams = query.order_by(Team.name).all()
        teams_data = []
        for team in teams:
            players_data = [{'id': player.id, 'name': player.name, 'is_pro_player': player.is_pro_player}
                            for player in team.players]
            team_info = {
                'id': team.id,
                'name': team.name,
                'company_name': team.company_name,
                'district_id': team.district_id,
                'district_name': team.district.name if team.district else None, # Access related District name
                'pro_player_count': team.pro_player_count,
                'players': players_data
            }
            teams_data.append(team_info)
        
        return jsonify(teams_data), 200

    except Exception as e:
        # Log the error e
        return jsonify({'error': 'Could not retrieve teams', 'message': str(e)}), 500

@team_bp.route('/teams/register', methods=['POST'])
def register_team():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    # Required fields
    team_name = data.get('team_name')
    district_id = data.get('district_id')
    players_data = data.get('players') # Expected to be a list of dicts

    # Validate required fields
    if not all([team_name, district_id, players_data]):
        return jsonify({'error': 'Missing required fields: team_name, district_id, players are required.'}), 400
    
    if not isinstance(players_data, list) or len(players_data) == 0 or len(players_data) > 7:
        return jsonify({'error': 'Players data must be a list containing 1 to 7 players.'}), 400

    # Validate district
    district = District.query.get(district_id)
    if not district:
        return jsonify({'error': 'Invalid district ID.'}), 400

    # Validate pro players count
    pro_player_count = 0
    for player_data in players_data:
        if not isinstance(player_data, dict) or 'name' not in player_data:
            return jsonify({'error': 'Each player must have a name.'}), 400
        if player_data.get('is_pro_player'):
            pro_player_count += 1
    
    if pro_player_count > 3:
        return jsonify({'error': 'A team can have a maximum of 3 pro players.'}), 400

    # Optional: Check for team name uniqueness (if desired)
    # if Team.query.filter_by(name=team_name).first():
    #     return jsonify({'error': 'Team name already exists.'}), 400

    company_name = data.get('company_name') # Optional
    # Captain details also optional based on form, but good to capture if provided
    # captain_name = data.get('captain_name') 
    # captain_email = data.get('captain_email')
    # captain_phone = data.get('captain_phone')

    try:
        new_team = Team(
            name=team_name,
            company_name=company_name,
            district_id=district_id,
            pro_player_count=pro_player_count
        )
        db.session.add(new_team)
        # Must flush to get new_team.id if players need it before commit,
        # or commit team first then add players.
        # For simplicity, let's assume cascade save works or we add players after team.id is available.
        # SQLAlchemy handles this if backref is set up correctly and team is added to player.

        for player_data in players_data:
            player_name = player_data.get('name')
            is_pro = player_data.get('is_pro_player', False)
            if player_name: # Only add players with names
                new_player = Player(name=player_name, is_pro_player=is_pro, team=new_team)
                db.session.add(new_player)
        
        db.session.commit()
        return jsonify({'message': 'Team registered successfully!', 'team_id': new_team.id}), 201

    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({'error': 'Could not register team', 'message': str(e)}), 500
