from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from base64 import b64decode
import xml.etree.ElementTree as ET
import mysql.connector
from dotenv import load_dotenv
import os

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
key = os.getenv('AES_KEY')
iv = os.getenv('AES_IV')

def decrypt_data(encrypted_data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(b64decode(encrypted_data))
    return decrypted_data.rstrip(b'\0').decode('utf-8')

def insert_data_to_db(data):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Insert user data
    cursor.execute("INSERT INTO User (name, username, location) VALUES (%s, %s, %s)", 
                   (data['name'], data['username'], data['location']))
    user_id = cursor.lastrowid

    # Insert demographics data
    cursor.execute("INSERT INTO Demographics (user_id, age, gender) VALUES (%s, %s, %s)", 
                   (user_id, data['age'], data['gender']))

    # Insert biometrics data
    cursor.execute("INSERT INTO Biometrics (user_id, height, weight) VALUES (%s, %s, %s)", 
                   (user_id, data['height'], data['weight']))

    # Insert medical conditions data
    cursor.execute("""
        INSERT INTO MedicalConditions (user_id, cardiovascular_disease, diabetes, respiratory_issues, 
                                       heat_sensitivity, kidney_disease, neurological_disorders, other_condition) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_id, data['medical_conditions']['cardiovascular_disease'], data['medical_conditions']['diabetes'], 
          data['medical_conditions']['respiratory_issues'], data['medical_conditions']['heat_sensitivity'], 
          data['medical_conditions']['kidney_disease'], data['medical_conditions']['neurological_disorders'], 
          data['medical_conditions']['other_condition']))

    # Insert medications data
    cursor.execute("""
        INSERT INTO Medications (user_id, diuretics, blood_pressure_medications, antihistamines, 
                                 antidepressants, antipsychotics, other_medication) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, data['medications']['diuretics'], data['medications']['blood_pressure_medications'], 
          data['medications']['antihistamines'], data['medications']['antidepressants'], 
          data['medications']['antipsychotics'], data['medications']['other_medication']))

    # Insert fluid intake data
    cursor.execute("""
        INSERT INTO FluidIntake (user_id, water_amount, electrolyte_drinks_amount, coconut_water_amount, 
                                 fruit_juice_amount, iced_tea_amount, soda_amount, milk_tea_amount, 
                                 coffee_amount, herbal_tea_amount, other_fluid, other_fluid_amount) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_id, data['fluid_intake']['water_amount'], data['fluid_intake']['electrolyte_drinks_amount'], 
          data['fluid_intake']['coconut_water_amount'], data['fluid_intake']['fruit_juice_amount'], 
          data['fluid_intake']['iced_tea_amount'], data['fluid_intake']['soda_amount'], 
          data['fluid_intake']['milk_tea_amount'], data['fluid_intake']['coffee_amount'], 
          data['fluid_intake']['herbal_tea_amount'], data['fluid_intake']['other_fluid'], 
          data['fluid_intake']['other_fluid_amount']))

    # Insert heat conditions data
    cursor.execute("""
        INSERT INTO HeatConditions (user_id, mild_dehydration, heat_rash, heat_stroke, muscle_fatigue, 
                                    heat_syncope, heat_edema, heat_exhaustion) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_id, data['heat_conditions']['mild_dehydration'], data['heat_conditions']['heat_rash'], 
          data['heat_conditions']['heat_stroke'], data['heat_conditions']['muscle_fatigue'], 
          data['heat_conditions']['heat_syncope'], data['heat_conditions']['heat_edema'], 
          data['heat_conditions']['heat_exhaustion']))

    # Insert activity data
    cursor.execute("""
        INSERT INTO Activity (user_id, previous_heat_issues, heat_issues_details, outdoor_activity, 
                              activity_level, activity_duration) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, data['previous_heat_issues'], data['heat_issues_details'], data['outdoor_activity'], 
          data['activity_level'], data['activity_duration']))

    conn.commit()
    cursor.close()
    conn.close()

@app.route('/receive_data', methods=['POST'])
def receive_data():
    encrypted_data = request.data
    decrypted_data = decrypt_data(encrypted_data)
    
    # Parse XML
    root = ET.fromstring(decrypted_data)
    data = {child.tag: child.text for child in root}

    # Insert data into the database
    insert_data_to_db(data)

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)