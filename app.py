from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///capycure.db'
app.config['JWT_SECRET_KEY'] = 'super-secret'
db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    clientID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    firstName = db.Column(db.String(80), unique=True, nullable=False)
    surname = db.Column(db.String(80), unique=True, nullable=False)
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    phoneNumber = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    MessageToUser = db.relationship('MessageToUser', uselist=False)
    MessageToTradesperson = db.relationship('MessageToTradesperson', uselist=False)

class TradesPerson(db.Model):
    tradesPersonID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    firstName = db.Column(db.String(80), unique=True, nullable=False)
    surname = db.Column(db.String(80), unique=True, nullable=False)
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    phoneNumber = db.Column(db.String(20), unique=True, nullable=False)
    trade = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    MessageToUser = db.relationship('MessageToUser', uselist=False)
    MessageToTradesperson = db.relationship('MessageToTradesperson', uselist=False)


class MessageToUser(db.Model):
    messageID = db.Column(db.Integer, primary_key=True)
    senderID = db.Column(db.Integer, db.ForeignKey('TradesPerson.tradesPersonID'), nullable=False)
    recipientID = db.Column(db.Integer, db.ForeignKey('User.clientID'), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    date_sent = db.Column(db.DateTime, nullable=False)


class MessageToTradesPerson(db.Model):
    messageID = db.Column(db.Integer, primary_key=True)
    senderID = db.Column(db.Integer, db.ForeignKey('User.clientID'), nullable=False)
    recipientID = db.Column(db.Integer, db.ForeignKey('TradesPerson.tradesPersonID'), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    date_sent = db.Column(db.DateTime, nullable=False)

class Review(db.Model):
    reviewID = db.Column(db.Integer, primary_key=True)
    subjectID = db.Column(db.Integer, db.ForeignKey('TradesPerson.tradesPersonID'), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('User.clientID'), nullable=False)
    review = db.Column(db.String(300), nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/api/signup', methods=['POST'])
def user_signup():
    data = request.get_json()

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_pw = generate_password_hash(data['password'])
    new_user = User(usernama=data['username'], firstName=data['firstName'], surname=data['surname'], email_address=data['email_address'], phoneNumber=data['phoneNumber'], trade=data['trade'], password_hash=hashed_pw)

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created!"}), 201


@app.route('/api/signup', methods=['POST'])
def tradesperson_signup():
    data = request.get_json()

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_pw = generate_password_hash(data['password'])
    new_user = User(usernama=data['username'], firstName=data['firstName'], surname=data['surname'], email_address=data['email_address'], phoneNumber=data['phoneNumber'], password_hash=hashed_pw)

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created!"}), 201


@app.route('/api/login', methods=['POST'])
def user_login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"token": access_token, "username": user.username}), 200

    return jsonify({"message": "Invalid credentials"}), 401


@app.route('/api/login', methods=['POST'])
def tradesperson_login():
    data = request.get_json()
    tradesperson = TradesPerson.query.filter_by(username=data['username']).first()

    if tradesperson and check_password_hash(tradesperson.password_hash, data['password']):
        access_token = create_access_token(identity=str(tradesperson.id))
        return jsonify({"token": access_token, "username": tradesperson.username}), 200

    return jsonify({"message": "Invalid credentials"}), 401





@app.route('/debug/users', methods=['GET'])
def list_users():
    users = User.query.all()

    user_list = [{"id": u.id, "username": u.username, "pw_hash": u.password_hash} for u in users]
    return jsonify(user_list)


@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({"username": user.username, "id": user.id})

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_tradesperson_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({"username": user.username, "id": user.id})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)