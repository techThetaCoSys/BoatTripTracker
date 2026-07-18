import os
import time
from datetime import datetime, timezone
from flask import Flask, Response, request, jsonify,send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "dist"),
    static_url_path="/"
)

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
        raw_body = request.get_data(as_text=True)

        if not raw_body or not raw_body.strip():
            return "Body not found", 400

        iso_string = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        data ="TimeStamp: "+ iso_string+"; Data: "+ raw_body

        latest_sensor_data = data
        print(data)
        print("POST request : data received")
        return "Got a post response"
        
    except Exception as err:
        print("Server error", err)
        return "Internal Server Error", 500
    
@app.route('/stream')
def stream():
    def event_stream():
        global latest_sensor_data
        while True:
            if(latest_sensor_data is not None):
                yield f"data: {latest_sensor_data}\n\n"
                latest_sensor_data = None
            time.sleep(1)
    return Response(event_stream(), mimetype='text/event-stream')
    
    




