from flask import Flask, jsonify, request, Response, render_template
import RPi.GPIO as GPIO
from datetime import datetime
from projectcode import call, motor_clockwise, motor_anticlockwise, cleanup
import requests
import threading 
import time
from picamera2 import Picamera2
import cv2

app = Flask(__name__)

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.set_controls({"AwbEnable": True, "AwbMode": 0})
picam2.start()

# Perth, Australia coordinates
LATITUDE = -31.952
LONGITUDE = 115.857

# Manaus, Brazil coordinates 
# LONGITUDE = -60.0217
# LATITUDE = -3.1190

# global variables
was_raining = False
was_above_300 = None
cover_extended = False
manual_mode = False

rain_expected = False
rain_hours = 0
weather_condition = None

def gen_frames():
    while True:
        frame = picam2.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        # Yield frame as byte string for MJPEG
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

def weather_updater():
    global rain_expected, rain_hours, weather_condition
    while True:
        rain_expected, rain_hours, weather_condition = weather()
        # Calculate seconds until next hour
        now = datetime.now()
        seconds_until_next_hour = (60 - now.minute) * 60 - now.second
        # Sleep until the next hour
        time.sleep(seconds_until_next_hour)

def rain_expected_next_12h(data):
    from datetime import datetime

    now = datetime.now()
    hourly_times = data['hourly']['time']   # list of ISO8601 strings
    precip = data['hourly']['precipitation']  # list of floats

    current_hour_str = now.strftime('%Y-%m-%dT%H:00')
    try:
        start_idx = next(i for i, t in enumerate(hourly_times) if t >= current_hour_str)
    except StopIteration:
        start_idx = 0  # fallback: start from beginning

    end_idx = min(start_idx + 12, len(precip))
    for offset, p in enumerate(precip[start_idx:end_idx]):
        if p > 0:
            return True, offset  # offset hours from now
    return False, None

def weathercode_to_symbol(wmo_code):
    # WMO code reference: https://open-meteo.com/en/docs#api_form
    if wmo_code == 0:
        return 'sunny'
    elif wmo_code in [1, 2, 3]:
        return 'partly-cloudy'
    elif wmo_code in [45, 48, 51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 71, 73, 75, 77, 80, 81, 82, 85, 86]:
        return 'cloudy'
    elif wmo_code in [61, 63, 65, 80, 81, 82]:
        return 'rainy'
    elif wmo_code in [71, 73, 75, 77, 85, 86]:
        return 'snowy'
    elif wmo_code in [95, 96, 99]:
        return 'rainy'  # Thunderstorm as rainy
    else:
        return 'unknown'  

def weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "temperature_2m,precipitation",
        "current_weather": True,
        "timezone": "Australia/Perth"
    }
    response = requests.get(url, params=params)
    data = response.json()

    current_code = data['current_weather']['weathercode']  # e.g., 0
    symbol = weathercode_to_symbol(current_code)
    rain_expected, rain_hours = rain_expected_next_12h(data)
    return rain_expected, rain_hours, symbol
    # return True, "rainy"

@app.route('/')
def home():
    return render_template('index_final.html')

@app.route('/api/status')
def api_status():
    global was_raining, was_above_300, cover_extended, weather_condition, rain_expected
    # Read sensor values
    rain_detected, sunlight = call()
    rain_hours = 0

    current_above_300 = sunlight > 300
    
    if ((current_above_300 and was_above_300 is not True) or (rain_detected and not was_raining)) and not manual_mode:
        motor_clockwise()
        cover_extended = True

    elif ((not current_above_300 and was_above_300 is True) or (not rain_detected and was_raining)) and not manual_mode:
        motor_anticlockwise()
        cover_extended = False

    was_raining = rain_detected
    was_above_300 = current_above_300

    return jsonify({
        "coverExtended": cover_extended,
        "sunlight": round(sunlight, 2),
        "rainDetected": rain_detected,
        "weatherCondition": weather_condition,
        "rainExpected": rain_expected,
        "rainHours": rain_hours
    })

@app.route('/api/control', methods=['POST'])
def api_control():
    global cover_extended
    command = request.json.get('command')
    if command == 'up' and not cover_extended:
        cover_extended = True
        motor_clockwise()
    elif command == 'down' and cover_extended:
        cover_extended = False
        motor_anticlockwise()
    return jsonify({"success": True})

@app.route('/api/set_mode', methods=['POST'])
def set_mode():
    global manual_mode
    data = request.get_json()
    mode = data.get('mode')
    if mode == 'manual':
        manual_mode = True
    elif mode == 'auto':
        manual_mode = False
    return jsonify({"success": True, "manualMode": manual_mode})

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    updater_thread = threading.Thread(target=weather_updater, daemon=True)
    updater_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)

