import os
import google.generativeai as genai
from dotenv import load_dotenv
import mysql.connector
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# Configure Google Generative AI (Gemini) API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Create the model
model = genai.GenerativeModel("gemini-1.5-flash")

# Connect to databases
def connect_to_database(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        logging.info(f"Connected to database {db_config['database']} successfully.")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to database {db_config['database']}: {err}")
        return None

db1_conn = connect_to_database(DATABASES['db1'])
db2_conn = connect_to_database(DATABASES['db2'])
db3_conn = connect_to_database(DATABASES['db3'])

# Fetch necessary data from databases
def fetch_data():
    try:
        cursor1 = db1_conn.cursor(dictionary=True)
        cursor2 = db2_conn.cursor(dictionary=True)
        cursor3 = db3_conn.cursor(dictionary=True)

        # Fetch user data from inet_ready_user
        cursor3.execute("SELECT u.user_id FROM User u JOIN UserProfile up ON u.user_id = up.user_id WHERE u.user_id = '21aa6f76-9e07-11ef-b354-54e1adccf4f3'")
        user_data = cursor3.fetchall()

        # Fetch weather data from inet_ready_system for 'Imus' city
        cursor2.execute("SELECT heat_index, inet_level FROM WeatherData WHERE city = %s", ('Imus',))
        weather_data = cursor2.fetchall()

        # Fetch medical data from inet_ready_ehr
        cursor1.execute("""
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
        medical_data = cursor1.fetchall()

        cursor1.close()
        cursor2.close()
        cursor3.close()

        return user_data, weather_data, medical_data
    except mysql.connector.Error as err:
        logging.error(f"Error fetching data: {err}")
        return None, None, None

# Function to get health advice from Gemini API
def get_health_advice_from_api(user_data, weather_data, medical_data):
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
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error fetching health advice: {e}")
        return None

def main():
    user_data, weather_data, medical_data = fetch_data()

    # Print fetched data for debugging
    logging.info(f"User Data: {user_data}")
    logging.info(f"Weather Data: {weather_data}")
    logging.info(f"Medical Data: {medical_data}")

    # Example usage
    if user_data and weather_data and medical_data:
        health_advice = get_health_advice_from_api(user_data[0], weather_data[0], medical_data[0])  # Assuming only one user for simplicity

        # Print the returned data from the API
        if health_advice:
            logging.info(f"Health Advice: {health_advice}")
        else:
            logging.warning("Failed to fetch health advice.")
    else:
        logging.warning("No valid data to fetch health advice.")

    # Close database connections
    if db1_conn:
        db1_conn.close()
    if db2_conn:
        db2_conn.close()
    if db3_conn:
        db3_conn.close()

if __name__ == "__main__":
    main()
