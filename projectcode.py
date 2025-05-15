from gpiozero import PWMOutputDevice, DigitalOutputDevice
import RPi.GPIO as GPIO
import smbus2
import time

GPIO.setmode(GPIO.BCM)
RAIN_SENSOR_PIN=14
GPIO.setup(RAIN_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

DIR1 = DigitalOutputDevice(17)
DIR2 = DigitalOutputDevice(27)
PWM1 = PWMOutputDevice(18)

VEML6030_ADDR = 0x10
bus = smbus2.SMBus(1)

def setup_hardware():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RAIN_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    DIR1 = DigitalOutputDevice(17)
    DIR2 = DigitalOutputDevice(27)
    PWM1 = PWMOutputDevice(18)

    bus = smbus2.SMBus(1)

def init_veml6030():
    try:
        bus.write_word_data(VEML6030_ADDR, 0x00, 0x0000)
        print(f"light sensor initiased at address 0x{VEML6030_ADDR:02x}")
        time.sleep(0.1)
    except Exception as e:
        print(f"error initialsing light sensor: {e}")
        
def read_light_sensor():
    try:
        data = bus.read_i2c_block_data(VEML6030_ADDR, 0x04, 2)
        raw = (data[1] << 8) | data[0]
        lux = raw * 0.0576
        print(f"Raw data: {data}, Calculated lux: {lux:.2f}")
        return lux
    except Exception as e:
        print(f"Error reading VEMl6030: {e}, returning 0 lux")
        return 0
            
def is_raining():
    return GPIO.input(RAIN_SENSOR_PIN) == GPIO.LOW

def motor_clockwise():
    print(f"motor clockwise")
    DIR1.on()
    DIR2.off()
    PWM1.value = 1.0
    time.sleep(1)
    DIR1.off()
    DIR2.off()
    PWM1.value = 0.0
    
def motor_anticlockwise():
    print(f"motor anticlockwise")
    DIR1.off()
    DIR2.on()
    PWM1.value = 1.0
    time.sleep(1)
    DIR1.off()
    DIR2.off()
    PWM1.value = 0.0
    
def cleanup():
    if DIR1: DIR1.close()
    if DIR2: DIR2.close()
    if PWM1: PWM1.close()
    if bus: bus.close()
    GPIO.cleanup()

def call():
    # setup_hardware()
    init_veml6030()
    rain_detected = is_raining()
    sunlight = read_light_sensor()
    # cleanup()
    return rain_detected, sunlight
    
# try:
    # init_veml6030()
    # print("Starting sensor monitoring...")
    # was_raining = False
    # was_above_300 = None
    
    # while True:
        # light_level = read_light_sensor()
        # raining = is_raining()
        # print(f"Light: {light_level:.2f} lux, Raining: {raining}")
        
        # current_above_300 = light_level > 300
        # current_raining = raining
        
        # if (current_above_300 and was_above_300 is not True) or (current_raining and not was_raining):
            # print("Condition(s) met")
            # motor_clockwise()
            
        # elif (not current_above_300 and was_above_300 is True) or (not current_raining and was_raining):
            # print("condition(s) not met")
            # motor_anticlockwise()
                  
        # was_above_300 = current_above_300    
        # was_raining = current_raining
        # time.sleep(0.1)
        
# except KeyboardInterrrupt:
    # print("Program stopped by user")
# finally:
    # DIR1.off()
    # DIR2.off()
    # PWM1.value = 0.0
    # GPIO.cleanup()
    # bus.close()
    # DIR1.close()
    # DIR2.close()
    # PWM1.close()
        
    
        
