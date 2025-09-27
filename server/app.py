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
    return jsonify({"you_sent": data})


@app.route("/label", methods=["POST"])
def post_label():
    data = request.get_json()
    key_id = data.get("keyId", None)
    assertion = data.get("assertion", None)
    proof = data.get("proof", None)
    public_inputs = data.get("publicInputs", None)
    if key_id is None or proof is None:
        return jsonify({"error": "Invalid Proof"}), 400
    if assertion is False:
        return jsonify({"error": "Assertion Failed"}), 400
    # TODO: add data to DB
    return 200


@app.route("/label", methods=["GET"])
def get_labels():
    city = request.args.get("city")
    level = request.args.get("level", "0")
    # print(city, level)
    results = generate_city_labels(city, level)
    # print(results)
    return jsonify({"data": results}), 200


if __name__ == "__main__":
    CORS(app)
    app.run(debug=True)
