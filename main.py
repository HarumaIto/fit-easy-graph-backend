import os
import sys
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, jsonify, request
from scraper import fetch_congestion_info
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

load_dotenv()

# MongoDBクライアント設定
try:
    # Create a new client and connect to the server
    MONGO_URI = os.getenv("MONGO_URI")
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
except Exception as e:
    print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
    sys.exit(1)

try:
    db = client.fit_easy_graph
    collection = db["congestion_info"]
except Exception as e:
    print("An authentication error was received. Are your username and password correct in your connection string?")
    sys.exit(1)

@app.route("/congestion", methods=["GET"])
def get_congestion():
    try:
        info = fetch_congestion_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route("/congestion", methods=["POST"])
def post_congestion():
    try:
        info = fetch_congestion_info()
        # 日本時間（JST: UTC+9）でtimestampを付与
        jst = timezone(timedelta(hours=9))
        doc = {
            "gym_id": "61",
            "gym_name": info.get("gym_name", "イオンタウン弥富店"),
            "timestamp": datetime.now(jst),
            "congestion_level": info.get("level"),
            # 必要に応じて天気なども追加可能
        }
        result = collection.insert_one(doc)
        return jsonify({"inserted_id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)