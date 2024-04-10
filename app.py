from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tu_base_de_datos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'tu_clave_secreta_jwt'
db = SQLAlchemy(app)
api = Api(app)
jwt = JWTManager(app)

class BlacklistEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    client_app_id = db.Column(db.String(36), nullable=False)
    blocked_reason = db.Column(db.String(255))
    ip_address = db.Column(db.String(15))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BlacklistEmail {self.email}>'

class AddToBlacklist(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_blacklist_email = BlacklistEmail(
                email=data['email'],
                client_app_id=data['app_uuid'],
                blocked_reason=data.get('blocked_reason', ''),
                ip_address=request.remote_addr
            )
            db.session.add(new_blacklist_email)
            db.session.commit()
            # Corrección: Retornar un diccionario en lugar de un objeto Response directamente
            return jsonify(created=True)
        except Exception as e:
            return jsonify(rejected=str(e))
    
class CheckBlacklist(Resource):
    def get(self, email):
        blacklist_email = BlacklistEmail.query.filter_by(email=email).first()
        if blacklist_email:
            return jsonify(is_blacklisted=True)
        else:
            return jsonify(is_blacklisted=False)

api.add_resource(AddToBlacklist, '/blacklist')
api.add_resource(CheckBlacklist, '/blacklist/<string:email>')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
