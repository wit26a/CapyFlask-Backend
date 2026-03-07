from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

gigs = [
    {"id": 1, "title": "Pipe fix", "price": 50, "seller": "Alice"},
    {"id": 2, "title": "Painting nursery", "price": 100, "seller": "Bobbi"}
]

@app.route('/api/gigs', methods=['GET'])
def get_gigs():
    return jsonify(gigs)

@app.route('/api/gigs', methods=['POST'])
def add_gig():
    new_data = request.json
    gigs.append(new_data)
    return jsonify({"message": "Gig added!"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
