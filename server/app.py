
from flask import Flask, jsonify, request
from flask_migrate import Migrate

from models import db, Pet

# create a Flask application instance
app = Flask(__name__)

# configure the database connection to the local file app.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# configure flag to disable modification tracking and use less memory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create a Migrate object to manage schema modifications
migrate = Migrate(app, db)

# initialize the Flask application to use the database
db.init_app(app)


# Home route
@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to Pawfect Match Pet Adoption API'
    })


# CREATE: Add a new pet
@app.route('/pets', methods=['POST'])
def create_pet():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'JSON data is required'}), 400

    name = data.get('name')
    species = data.get('species')

    if not name or not species:
        return jsonify({
            'error': 'Name and species are required'
        }), 400

    if len(name) > 50:
        return jsonify({
            'error': 'Name must be 50 characters or fewer'
        }), 400

    pet = Pet(name=name, species=species)

    try:
        db.session.add(pet)
        db.session.commit()
        return jsonify(pet.to_dict()), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Could not create pet'}), 500


# READ: Get all pets
@app.route('/pets', methods=['GET'])
def get_pets():
    pets = Pet.query.all()
    return jsonify([pet.to_dict() for pet in pets]), 200


# READ: Get one pet by ID
@app.route('/pets/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    pet = db.session.get(Pet, pet_id)

    if pet is None:
        return jsonify({'error': 'Pet not found'}), 404

    return jsonify(pet.to_dict()), 200


# UPDATE: Update a pet
@app.route('/pets/<int:pet_id>', methods=['PATCH'])
def update_pet(pet_id):
    pet = db.session.get(Pet, pet_id)

    if pet is None:
        return jsonify({'error': 'Pet not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'error': 'JSON data is required'}), 400

    name = data.get('name', pet.name)
    species = data.get('species', pet.species)

    if not isinstance(name, str) or not name.strip():
        return jsonify({'error': 'Name must be a non-empty string'}), 400

    if len(name) > 50:
        return jsonify({
            'error': 'Name must be 50 characters or fewer'
        }), 400

    if not isinstance(species, str) or not species.strip():
        return jsonify({
            'error': 'Species must be a non-empty string'
        }), 400

    pet.name = name.strip()
    pet.species = species.strip()

    try:
        db.session.commit()
        return jsonify(pet.to_dict()), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Could not update pet'}), 500


# DELETE: Remove a pet
@app.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    pet = db.session.get(Pet, pet_id)

    if pet is None:
        return jsonify({'error': 'Pet not found'}), 404

    try:
        db.session.delete(pet)
        db.session.commit()
        return jsonify({
            'message': 'Pet deleted successfully'
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Could not delete pet'}), 500


if __name__ == '__main__':
    app.run(port=5555, debug=True)