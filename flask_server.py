from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ESP32 IP Address (Change accordingly)
ESP32_URL = "http://192.168.1.100/update"

@app.route('/update_data', methods=['POST'])
def update_data():
    data = request.json
    print("Received Data:", data)

    try:
        # Send Data to ESP32
        response = requests.post(ESP32_URL, json=data)
        return jsonify({"status": "success", "esp_response": response.text})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
