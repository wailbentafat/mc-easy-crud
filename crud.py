
from flask import Flask, json, jsonify, request, make_response,Response
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, ValidationError, fields

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Personality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"<Personality(id={self.id}, firstname='{self.firstname}', lastname='{self.lastname}', type='{self.type}', age={self.age})>"
    
    
class PersonalitySchema(Schema):
    id = fields.Int(dump_only=True)
    firstname = fields.Str(required=True)
    lastname = fields.Str(required=True)
    type = fields.Str(required=True)
    age = fields.Int(required=True)    
    


  

class PersonalitiesResource(Resource):
    def get(self, personality_id=None):
        if personality_id is None:
            personalities = Personality.query.all()
            personalities_data = [
                {
                    'id': personality.id,
                    'firstname': personality.firstname,
                    'lastname': personality.lastname,
                    'type': personality.type,
                    'age': personality.age
                } for personality in personalities
            ]
            response = make_response(json.dumps({"personalities": personalities_data}), 200)
            response.mimetype = 'application/json'
            return response
        else:
            #
            personality = Personality.query.get(personality_id)
            if not personality:
                response = make_response(json.dumps({"message": "Personality not found"}), 404)
                response.mimetype = 'application/json'
                return response
            else:
                personality_data = {
                    'id': personality.id,
                    'firstname': personality.firstname,
                    'lastname': personality.lastname,
                    'type': personality.type,
                    'age': personality.age
                }
                response = make_response(json.dumps({"personality": personality_data}), 200)
                response.mimetype = 'application/json'
                return response

    def post(self):
        
        data = request.get_json()
        new_personality = Personality(
            firstname=data['firstname'],
            lastname=data['lastname'],
            type=data['type'],
            age=data['age']
        )
        ##print(data)
        ##print(new_personality)
        existing_personality = Personality.query.filter_by(firstname=data['firstname']).first()
        ##print(existing_personality)
        if existing_personality:
            response = make_response(json.dumps({"message": "Personality already exists"}), 409)
            response.mimetype = 'application/json'
            return response
        
        ##print('were here')
        db.session.add(new_personality)
        db.session.commit()
       ## print('success')
        
        personality_schema = PersonalitySchema()
        serialized_personality = personality_schema.dump(new_personality)
        ##print(serialized_personality) 
        response = make_response(json.dumps({"personality": serialized_personality}), 201)
        response.mimetype = 'application/json'
        ##print(response)
        return response
    def delete(self, personality_id):
        personality = Personality.query.get(personality_id)
        if not personality:
            response = make_response(json.dumps({"message": "Personality not found"}), 404)
            response.mimetype = 'application/json'
            return response
        else:
            db.session.delete(personality)
            db.session.commit()
            response = make_response(json.dumps({"message": "Personality deleted"}), 200)
            response.mimetype = 'application/json'
            return response
    def put(self, personality_id):
        data = request.get_json()
        personality = Personality.query.get(personality_id)
        if not personality:
            response = make_response(json.dumps({"message": "Personality not found"}), 404)
            response.mimetype = 'application/json'
            return response
        else:
            personality.firstname = data['firstname']
            personality.lastname = data['lastname']
            personality.type = data['type']
            personality.age = data['age']
            db.session.commit()
            response = make_response(json.dumps({"message": "Personality updated"}), 200)
            response.mimetype = 'application/json'
            return response          
        

    
api.add_resource(PersonalitiesResource, '/personalities', '/personalities/<int:personality_id>')
with app.app_context():
    db.create_all()
if __name__ == '__main__':

    app.run(debug=True)
