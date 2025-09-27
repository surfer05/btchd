from flask import Flask, jsonify, request
from flask_cors import CORS
from server.labels import generate_city_labels


app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, Flask!"


@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json()
    return jsonify({"Data": data})


@app.route("/label", methods=["POST"])
def post_label():
    data = request.get_json()
    # {'proofHex': '0x', 'review': {'categories': ['Location'], 'text': 'Beta', 'rating': 5}, 'expiresAt': 1759007394, 'publicInputsHex': '0x', 'geohash7': 'ttnf3nz'}
    proof = data.get("proof", None)
    if proof is None:
        return "Proof not found", 400
    review = data.get("review", None)
    if review is None:
        return "Review is empty", 400
    label = review.get("text")
    categories = review.get("categories")
    rating = review.get("rating")
    # TODO: add data to DB
    return "Review successful", 200


@app.route("/label", methods=["GET"])
def get_labels():
    city = request.args.get("city")
    level = request.args.get("level", "0")
    results = generate_city_labels(city, level)
    return jsonify({"data": results}), 200


if __name__ == "__main__":
    CORS(app)
    app.run(debug=True)
