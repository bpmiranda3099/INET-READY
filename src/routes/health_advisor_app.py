import os
import time
from dotenv import load_dotenv
import mysql.connector
from flask import Flask, request, jsonify
from loguru import logger
from groq import Groq
import google.generativeai as genai
from functools import lru_cache
import xml.etree.ElementTree as ET

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "routes_log", "health_advisor.log"))
logger.add(log_file_path, level="INFO", format="{time} - {level} - {message}")

# Initialize Flask app
app = Flask(__name__)

# Database credentials
DATABASES = {
    'db1': {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    },
    'db2': {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME_2')
    },
    'db3': {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME_3')
    }
}

# Configure Groq API
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Configure Google Generative AI (Gemini) API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Connect to databases with caching
@lru_cache(maxsize=None)
def connect_to_database(db_config_tuple):
    db_config = dict(db_config_tuple)
    try:
        conn = mysql.connector.connect(**db_config)
        logger.info(f"Connected to database {db_config['database']} successfully.")
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Error connecting to database {db_config['database']}: {err}")
        return None

db1_conn = connect_to_database(tuple(DATABASES['db1'].items()))
db2_conn = connect_to_database(tuple(DATABASES['db2'].items()))
db3_conn = connect_to_database(tuple(DATABASES['db3'].items()))

# Fetch necessary data from databases with caching
@lru_cache(maxsize=None)
def fetch_user_data(user_id):
    try:
        cursor = db3_conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT u.user_id FROM User u JOIN UserProfile up ON u.user_id = up.user_id WHERE u.user_id = %s",
            (user_id,)
        )
        user_data = cursor.fetchall()
        cursor.close()
        return user_data
    except mysql.connector.Error as err:
        logger.error(f"Error fetching user data: {err}")
        return None

@lru_cache(maxsize=None)
def fetch_weather_data(city):
    try:
        cursor = db2_conn.cursor(dictionary=True)
        cursor.execute("SELECT heat_index, heat_level FROM WeatherData WHERE city = %s", (city,))
        weather_data = cursor.fetchall()
        cursor.close()
        return weather_data
    except mysql.connector.Error as err:
        logger.error(f"Error fetching weather data: {err}")
        return None

@lru_cache(maxsize=None)
def fetch_medical_data(user_id):
    try:
        cursor = db1_conn.cursor(dictionary=True)
        cursor.execute(""" 
            SELECT mc.user_id, mc.cardiovascular_disease, mc.diabetes, mc.respiratory_issues, mc.heat_sensitivity, mc.kidney_disease, mc.neurological_disorders, mc.other_condition,
                   b.height, b.weight,
                   d.age, d.gender,
                   m.diuretics, m.blood_pressure_medications, m.antihistamines, m.antidepressants, m.antipsychotics, m.other_medication,
                   f.water_amount, f.electrolyte_drinks_amount, f.coconut_water_amount, f.fruit_juice_amount, f.iced_tea_amount, f.soda_amount, f.milk_tea_amount, f.coffee_amount, f.herbal_tea_amount, f.other_fluid, f.other_fluid_amount,
                   h.mild_dehydration, h.heat_rash, h.heat_stroke, h.muscle_fatigue, h.heat_syncope, h.heat_edema, h.heat_exhaustion,
                   a.previous_heat_issues, a.heat_issues_details, a.outdoor_activity, a.activity_level, a.activity_duration
            FROM MedicalConditions mc
            JOIN Biometrics b ON mc.user_id = b.user_id
            JOIN Demographics d ON mc.user_id = d.user_id
            JOIN Medications m ON mc.user_id = m.user_id
            JOIN FluidIntake f ON mc.user_id = f.user_id
            JOIN HeatConditions h ON mc.user_id = h.user_id
            JOIN Activity a ON mc.user_id = a.user_id
            WHERE mc.user_id = %s
        """, (user_id,))
        medical_data = cursor.fetchall()
        cursor.close()
        return medical_data
    except mysql.connector.Error as err:
        logger.error(f"Error fetching medical data: {err}")
        return None

# Function to get health advice from Groq API
def get_health_advice_from_groq(prompt):
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[ 
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error fetching health advice from Groq: {e}")
        return None

# Function to get health advice from Gemini API
def get_health_advice_from_gemini(prompt):
    try:
        response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error fetching health advice from Gemini: {e}")
        return None

# Function to get structured health advice with retry logic
def get_health_advice(user_data, weather_data, medical_data, city):
    data = {
        "User Data": user_data,
        "Weather Data": weather_data,
        "Medical Data": medical_data
    }
    prompt = f"""
    Health Advisory System (STRICTLY follow the format 1-4 and the legal compliance, including data privacy regulations)

    Provide a friendly and concise health advice based on the following data, divided into sections, while ensuring compliance with relevant national health standards, including data privacy regulations and health recommendations. Concisely explain the purpose of the system, ensuring that the user is informed that their health data is being used to generate the advice and that all personal information is handled according to the Data Privacy Act of 2012 (for users in the Philippines) or applicable regulations (for users outside the country).
    
    This is the format:
    1. INET-READY: based on the data, state if the user is ready for travel in {city} or not by saying INET-READY or NOT INET-READY or NOT INET-READY.

    2. Important Notice: Make it one sentence concise.

    3. Current Conditions: Describe the current heat index and weather based on the user's travel destination (state the city provided in the data). Ensure that the system communicates the data in simple terms, adhering to the National Health Standards for public health communication.

    4. Health Risk Assessment: Give 1-2 sentences health assessment risks based on the user's medical data directly, while adhering to ethical standards of medical data usage. Ensure that the information complies with legal requirements like informed consent and the appropriate use of health data.

    5. Personalized Advice: Offer 5 non-redundant and insightful personalized health (strictly adhere to this) but avoid numbering tips based on the user's risk factors. Ensure that advice aligns with national health guidelines (e.g., recommendations from the Department of Health in the Philippines or relevant health authorities in other jurisdictions). The system should not provide medical diagnoses or replace professional healthcare advice.

    6. General Precautions: List general heat safety tips, such as staying hydrated, avoiding prolonged exposure to direct sunlight, and recognizing heat-related illnesses. The tips should align with public health standards set by national health organizations.

    The response should be like this:
    The AI shouldn't say anything. Just the following format:

    INET-READY:\nINET-READY or NOT INET-READY
    Important Notice:\n<text here>
    Current Conditions:\n<text here>
    Health Risk Assessment:\n<text here>
    Personalized Advice:\n<concise item list one here (no bullets, no numbering)>
                        \n<concise item list two here (no bullets, no numbering)>
                        \n<concise item list three here (no bullets, no numbering)>
                        \n<concise item list four here (no bullets, no numbering)>
                        \n<concise item list five here (no bullets, no numbering)>
    General Precautions:\n<list here (no bullets, no numbering)>
    Conclusion(but don't include the conclusion word)\n

    Nothing else, nothing more. No new line, no extra spaces. Just the text.
    {data, 'planned travel destination', city}
    """
    
    groq_advice = get_health_advice_from_groq(prompt)
    if groq_advice:
        return groq_advice

    gemini_advice = get_health_advice_from_gemini(prompt)
    if gemini_advice:
        return gemini_advice

    return {"error": "Could not generate health advice"}

# Health Advisory API endpoint
@app.route("/get_health_advisory", methods=["POST"])
def health_advice_route():
    try:
        # Parse the XML request data
        request_data = request.data.decode("utf-8")
        root = ET.fromstring(request_data)

        city = root.find("city").text
        user_id = root.find("user_id").text
        
        user_data = fetch_user_data(user_id)
        weather_data = fetch_weather_data(city)
        medical_data = fetch_medical_data(user_id)

        health_advice = get_health_advice(user_data, weather_data, medical_data, city)

        return jsonify({"advisory": health_advice})
    
    except Exception as e:
        logger.error(f"Error processing health advice request: {e}")
        return jsonify({"error": "An error occurred while processing the request."}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
