from flask import Flask, jsonify, request
from flask_cors import CORS

from aimodel import predict_phishing


app = Flask(__name__)

# Allow cross-origin requests from the same origin (deployed frontend uses the same domain via the /api rewrite)
# Using default CORS settings to accept requests from the frontend served by Vercel.
CORS(app)


@app.route("/")
def status():
    return "Phishing detector backend is running."


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "The request must contain JSON data."
        }), 400

    message = data.get("message")

    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "error": "Please enter a message."
        }), 400

    try:
        prediction = predict_phishing(message)
        return jsonify(prediction), 200

    except FileNotFoundError as error:
        return jsonify({
            "error": str(error)
        }), 503

    except (TypeError, ValueError) as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception:
        app.logger.exception("Prediction failed.")

        return jsonify({
            "error": "The message could not be analyzed."
        }), 500


# Support requests routed to /api/* by the Vercel rewrite. The frontend posts to /api/analyze
# so provide an alias endpoint that calls the same handler.
@app.route('/api/analyze', methods=['POST'])
def analyze_api():
    return analyze()


if __name__ == "__main__":
    app.run(debug=True)