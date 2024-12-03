import time
import adafruit_dht
import board
import RPi.GPIO as GPIO
from hx711 import HX711

# Initialize two DHT22 sensors
dht_device1 = adafruit_dht.DHT22(board.D22, use_pulseio=False)
dht_device2 = adafruit_dht.DHT22(board.D18, use_pulseio=False)

# Initialize GPIO pins for HX711 module (Load sensor)
hx711_dout = 5    # DOUT pin (Data Pin)
hx711_pd_sck = 6  # PD_SCK pin (Clock Pin)

# Set GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Setup GPIO pins
GPIO.setup(hx711_dout, GPIO.IN)
GPIO.setup(hx711_pd_sck, GPIO.OUT)

# Create HX711 object (Set gain during initialization)
hx711 = HX711(dout_pin=hx711_dout, pd_sck_pin=hx711_pd_sck, gain=64)

# Reset the HX711 module
hx711.reset()

# Wait for the sensor to stabilize
time.sleep(2)

# Calibration factor (you need to find this manually by placing a known weight on the load cell)
calibration_factor = 800000  # Adjust this value after calibration

# Function to convert raw data to weight in kg
def raw_to_kg(raw_data, calibration_factor):
    average_raw = sum(raw_data) / len(raw_data)
    return average_raw / calibration_factor

# Function to read data from DHT22 sensors
def read_dht22():
    try:
        # Read data from the first sensor
        temperature_c1 = dht_device1.temperature
        humidity1 = dht_device1.humidity

        # Read data from the second sensor
        temperature_c2 = dht_device2.temperature
        humidity2 = dht_device2.humidity

        # Return the readings
        return temperature_c1, humidity1, temperature_c2, humidity2
    except RuntimeError as err:
        print(f"RuntimeError: {err.args[0]}")
        return None, None, None, None

# Function to read load sensor
def read_load_sensor():
    try:
        # Get raw data from HX711
        raw_data = hx711.get_raw_data()
        if raw_data:
            # Convert raw data to kg
            weight_in_kg = raw_to_kg(raw_data, calibration_factor)
            return weight_in_kg
        else:
            return None
    except Exception as e:
        print(f"Error reading load sensor: {e}")
        return None

# Main loop
try:
    while True:
        # Read sensor data
        temperature_c1, humidity1, temperature_c2, humidity2 = read_dht22()
        weight = read_load_sensor()

        # Only print if data is valid
        if temperature_c1 is not None and humidity1 is not None and temperature_c2 is not None and humidity2 is not None and weight is not None:
            print(f"Sensor 1 - Temp: {temperature_c1:.1f}°C, Humidity: {humidity1:.1f}%")
            print(f"Sensor 2 - Temp: {temperature_c2:.1f}°C, Humidity: {humidity2:.1f}%")
            print(f"Weight: {weight:.3f} kg")
        else:
            print("Error with sensors!")

        time.sleep(60)  # Delay before updating the outputs

except KeyboardInterrupt:
    print("Measurement stopped.")

finally:
    GPIO.cleanup()  # Clean up GPIO pins
