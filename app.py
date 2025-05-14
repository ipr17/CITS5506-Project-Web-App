from flask import Flask, jsonify, request, Response, render_template
import RPi.GPIO as GPIO
from datetime import datetime
from projectcode import init_veml6030, read_light_sensor, is_raining, motor_clockwise, motor_anticlockwise
# Import your sensor and camera libraries here

app = Flask(__name__)

was_raining = False
was_above_300 = None

@app.route('/')
def home():
    return render_template('index_final.html')

@app.route('/api/status')
def api_status():
    # Read sensor values
    cover_extended = True #TODO
    sunlight = read_light_sensor()
    rain_detected = is_raining()
    weather_condition = "sunny"
    rain_expected = False
    rain_hours = 0

    current_above_300 = sunlight > 300
    
    if (current_above_300 and was_above_300 is not True) or (rain_detected and not was_raining):
        print("Condition(s) met")
        motor_clockwise()

    elif (not current_above_300 and was_above_300 is True) or (not rain_detected and was_raining):
        print("Condition(s) not met")
        motor_anticlockwise()

    was_raining = rain_detected
    was_above_300 = current_above_300

    return jsonify({
        "coverExtended": cover_extended,
        "sunlight": sunlight,
        "rainDetected": rain_detected,
        "weatherCondition": weather_condition,
        "rainExpected": rain_expected,
        "rainHours": rain_hours
    })

@app.route('/api/control', methods=['POST'])
def api_control():
    command = request.json.get('command')
    # Handle the command (extend/retract cover, manual close, etc.)
    # Your code to control the hardware
    return jsonify({"success": True})

@app.route('/video_feed')
def video_feed():
    return "Video feed not implemented yet", 501

if __name__ == '__main__':
    init_veml6030()
    app.run(host='0.0.0.0', port=5000, debug=True)
