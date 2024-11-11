from flask import Flask, request, jsonify
from Cryptodome.Cipher import AES 
from base64 import b64decode
import xml.etree.ElementTree as ET
import mysql.connector
from dotenv import load_dotenv
import os
import re
from threading import Thread, Lock
from functools import lru_cache
from queue import Queue
import logging
import time

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Database configuration
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

# AES key and IV (must match the Dart side)
key = os.getenv('AES_KEY').encode('utf-8')
iv = os.getenv('AES_IV').encode('utf-8')

# Queue for batch processing
data_queue = Queue()
batch_size = 10
lock = Lock()

# Set up logging
logging.basicConfig(level=logging.INFO)
process_log_path = r'C:\Users\brand\OneDrive - Lyceum of the Philippines University\Projects\INET-READY\src\routes\routes_log\process.log'
query_log_path = r'C:\Users\brand\OneDrive - Lyceum of the Philippines University\Projects\INET-READY\src\database\inet_ready_ehr\ehr_logs\query.log'

def decrypt_data(encrypted_data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(b64decode(encrypted_data))
    return decrypted_data.rstrip(b'\0').decode('utf-8')

@lru_cache(maxsize=128)
def validate_data(data):
    # Add your validation logic here
    if not re.match(r'^[a-zA-Z0-9_]+$', data['username']):
        raise ValueError("Invalid username")
    # Add more validation as needed

def insert_data_to_db(data_batch):
    start_time = time.time()
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for data in data_batch:
            # Insert user data
            cursor.execute("INSERT INTO User (user_id, name, username, location) VALUES (%s, %s, %s, %s)", 
                           (data['user_id'], data['name'], data['username'], data['location']))
            user_id = data['user_id']

            # Insert demographics data
            cursor.execute("INSERT INTO Demographics (user_id, age, gender) VALUES (%s, %s, %s)", 
                           (user_id, data['demographics']['age'], data['demographics']['gender']))

            # Insert biometrics data
            cursor.execute("INSERT INTO Biometrics (user_id, height, weight) VALUES (%s, %s, %s)", 
                           (user_id, data['biometrics']['height'], data['biometrics']['weight']))

            # Insert medical conditions data
            cursor.execute("INSERT INTO MedicalConditions (user_id, cardiovascular_disease, diabetes, respiratory_issues, heat_sensitivity, kidney_disease, neurological_disorders, other_condition) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                           (user_id, data['medical_conditions']['cardiovascular_disease'], data['medical_conditions']['diabetes'], data['medical_conditions']['respiratory_issues'], data['medical_conditions']['heat_sensitivity'], data['medical_conditions']['kidney_disease'], data['medical_conditions']['neurological_disorders'], data['medical_conditions']['other_condition']))

            # Insert medications data
            cursor.execute("INSERT INTO Medications (user_id, diuretics, blood_pressure_medications, antihistamines, antidepressants, antipsychotics, other_medication) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                           (user_id, data['medications']['diuretics'], data['medications']['blood_pressure_medications'], data['medications']['antihistamines'], data['medications']['antidepressants'], data['medications']['antipsychotics'], data['medications']['other_medication']))

            # Insert fluid intake data
            cursor.execute("INSERT INTO FluidIntake (user_id, water_amount, electrolyte_drinks_amount, coconut_water_amount, fruit_juice_amount, iced_tea_amount, soda_amount, milk_tea_amount, coffee_amount, herbal_tea_amount, other_fluid, other_fluid_amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                           (user_id, data['fluid_intake']['water_amount'], data['fluid_intake']['electrolyte_drinks_amount'], data['fluid_intake']['coconut_water_amount'], data['fluid_intake']['fruit_juice_amount'], data['fluid_intake']['iced_tea_amount'], data['fluid_intake']['soda_amount'], data['fluid_intake']['milk_tea_amount'], data['fluid_intake']['coffee_amount'], data['fluid_intake']['herbal_tea_amount'], data['fluid_intake']['other_fluid'], data['fluid_intake']['other_fluid_amount']))

            # Insert heat conditions data
            cursor.execute("INSERT INTO HeatConditions (user_id, mild_dehydration, heat_rash, heat_stroke, muscle_fatigue, heat_syncope, heat_edema, heat_exhaustion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                           (user_id, data['heat_conditions']['mild_dehydration'], data['heat_conditions']['heat_rash'], data['heat_conditions']['heat_stroke'], data['heat_conditions']['muscle_fatigue'], data['heat_conditions']['heat_syncope'], data['heat_conditions']['heat_edema'], data['heat_conditions']['heat_exhaustion']))

            # Insert activity data
            cursor.execute("INSERT INTO Activity (user_id, previous_heat_issues, heat_issues_details, outdoor_activity, activity_level, activity_duration) VALUES (%s, %s, %s, %s, %s, %s)", 
                           (user_id, data['activity']['previous_heat_issues'], data['activity']['heat_issues_details'], data['activity']['outdoor_activity'], data['activity']['activity_level'], data['activity']['activity_duration']))

        conn.commit()
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    logging.info(f"Batch processed in {time.time() - start_time} seconds")

def batch_processor():
    while True:
        data_batch = []
        while not data_queue.empty() and len(data_batch) < batch_size:
            data_batch.append(data_queue.get())
        if data_batch:
            insert_data_to_db(data_batch)

@app.route('/receive_data', methods=['POST'])
def receive_data():
    start_time = time.time()
    encrypted_data = request.data
    decrypted_data = decrypt_data(encrypted_data)
    
    # Parse XML
    root = ET.fromstring(decrypted_data)
    data = {}
    for child in root:
        if list(child):
            data[child.tag] = {subchild.tag: subchild.text for subchild in child}
        else:
            data[child.tag] = child.text

    try:
        validate_data(data)
        with lock:
            data_queue.put(data)
        elapsed_time = time.time() - start_time
        logging.info(f"Data received and validated in {elapsed_time:.2f} seconds", extra={'logfile': query_log_path})
        return jsonify({'status': 'success'}), 200
    except ValueError as e:
        logging.error(f"Validation error: {e}", extra={'logfile': query_log_path})
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    processor_thread = Thread(target=batch_processor, daemon=True)
    processor_thread.start()
    app.run(debug=True, ssl_context='adhoc')  # Use SSL for HTTPS