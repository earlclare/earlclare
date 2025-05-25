# backend/routes/district_routes.py
from flask import Blueprint, jsonify
from backend.models import District # Assuming models/__init__.py makes District accessible

district_bp = Blueprint('district_bp', __name__)

@district_bp.route('/districts', methods=['GET'])
def get_districts():
    try:
        districts = District.query.all()
        districts_data = [{'id': district.id, 'name': district.name} for district in districts]
        return jsonify(districts_data), 200
    except Exception as e:
        # Log the error e
        return jsonify({'error': 'Could not retrieve districts', 'message': str(e)}), 500
