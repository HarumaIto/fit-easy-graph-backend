from flask import Flask, jsonify
from scraper import fetch_congestion_info

app = Flask(__name__)

@app.route("/congestion", methods=["GET"])
def get_congestion():
    try:
        info = fetch_congestion_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)