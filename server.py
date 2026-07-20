import os
import time
from datetime import datetime, timezone
from flask import Flask, Response, request, jsonify,send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "dist"),
    static_url_path="/"
)
CORS(app)

latest_sensor_data = None

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_catch_all(path):
    if path.startswith("api/"):
        return jsonify({"success": False, "error": "Not Found"}), 404
        
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
        
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api",methods=["POST"],strict_slashes=False)
def post_metrics():
    try:
        global latest_sensor_data 
        raw_body = request.get_data()
        print(raw_body)

        if not raw_body.lat or not raw_body.lon:
            return "Incorrect data format", 400

        iso_string = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        data ="TimeStamp: "+ iso_string+"; Data: "+ raw_body
        
        latest_sensor_data = jsonify({
            "latitude":raw_body.lat,
            "longitude" :raw_body.lon,
            "altitude":raw_body.alt,
            "phone":raw_body.phone,
            "device_time":raw_body.time,
            "time":iso_string,
        })
        
        print("POST request : data received")
        return "Got a post response"
        
    except Exception as err:
        print("Server error", err)
        return "Internal Server Error", 500
    
@app.route('/getData', methods=['GET'],strict_slashes=False)
def getData():
    try:
        global latest_sensor_data
        if latest_sensor_data is not None:
            print(latest_sensor_data)
            data = latest_sensor_data
            latest_sensor_data = None
            return jsonify({"success": True, "data": data}), 200
        else:
            return jsonify({"success": False, "error": "No new data available"}), 404
    except Exception as err:
        print("Server error", err)
        return jsonify({"success": False, "error": "Internal Server Error"}), 500
    
    
    




