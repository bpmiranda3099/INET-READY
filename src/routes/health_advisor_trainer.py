import os
import time
import threading
from dotenv import load_dotenv
import mysql.connector
from loguru import logger
from groq import Groq
import google.generativeai as genai
from functools import lru_cache

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "routes_log", "health_advisor.log"))
logger.add(log_file_path, level="INFO", format="{time} - {level} - {message}")

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
def fetch_user_data():
    try:
        cursor = db3_conn.cursor(dictionary=True)
        cursor.execute("SELECT u.user_id FROM User u JOIN UserProfile up ON u.user_id = up.user_id WHERE u.user_id = '21aa6f76-9e07-11ef-b354-54e1adccf4f3'")
        user_data = cursor.fetchall()
        cursor.close()
        return user_data
    except mysql.connector.Error as err:
        logger.error(f"Error fetching user data: {err}")
        return None

@lru_cache(maxsize=None)
def fetch_weather_data():
    try:
        cursor = db2_conn.cursor(dictionary=True)
        cursor.execute("SELECT heat_index, heat_level FROM WeatherData WHERE city = %s", ('Imus',))
        weather_data = cursor.fetchall()
        cursor.close()
        return weather_data
    except mysql.connector.Error as err:
        logger.error(f"Error fetching weather data: {err}")
        return None

@lru_cache(maxsize=None)
def fetch_medical_data():
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
            WHERE mc.user_id = '21aa6f76-9e07-11ef-b354-54e1adccf4f3'
        """)
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
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error fetching health advice from Gemini: {e}")
        return None

# Function to get health advice with retry logic
def get_health_advice(user_data, weather_data, medical_data):
    data = {
        "User Data": user_data,
        "Weather Data": weather_data,
        "Medical Data": medical_data
    }
    prompt = f"""
    Provide a friendly and concise health advice based on the following data, divided into sections:

    1. Introduction: Briefly explain the purpose of the system.
    2. Current Conditions: Describe the current heat index and weather.
    3. Health Risk Assessment: Assess health risks from the user's medical data.
    4. Personalized Advice: Give personalized health tips.
    5. General Precautions: List general heat safety tips.

    Data: {data}
    """

    for _ in range(3):
        advice = get_health_advice_from_groq(prompt)
        if advice:
            return advice
        time.sleep(5)

    for _ in range(3):
        advice = get_health_advice_from_gemini(prompt)
        if advice:
            return advice
        time.sleep(5)

    logger.error("Failed to fetch health advice from both APIs.")
    return None

def main():
    start_time = time.time()
    logger.info("Starting the health advisor process.")

    # Use threading to fetch data concurrently
    user_data_thread = threading.Thread(target=fetch_user_data)
    weather_data_thread = threading.Thread(target=fetch_weather_data)
    medical_data_thread = threading.Thread(target=fetch_medical_data)

    user_data_thread.start()
    weather_data_thread.start()
    medical_data_thread.start()

    user_data_thread.join()
    weather_data_thread.join()
    medical_data_thread.join()

    user_data = fetch_user_data()
    weather_data = fetch_weather_data()
    medical_data = fetch_medical_data()

    # Example usage
    if user_data and weather_data and medical_data:
        health_advice = get_health_advice(user_data[0], weather_data[0], medical_data[0])  # Assuming only one user for simplicity

        # Print the returned data from the API
        if health_advice:
            print("Health Advice:", health_advice)
            logger.info("Health advice fetched successfully.")
        else:
            logger.warning("Failed to fetch health advice.")
    else:
        logger.warning("No valid data to fetch health advice.")

    # Close database connections
    if db1_conn:
        db1_conn.close()
    if db2_conn:
        db2_conn.close()
    if db3_conn:
        db3_conn.close()
    logger.info("Health advisor process completed.")
    
    end_time = time.time()
    total_time = end_time - start_time
    logger.info(f"Total time taken for the process to complete: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()