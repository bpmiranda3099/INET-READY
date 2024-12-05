from flask import Flask, request, jsonify
import os
import mysql.connector
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

@app.route('/get_cities', methods=['GET'])
def get_cities():
    # Connect to the database
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME_2')
    )
    cursor = conn.cursor(dictionary=True)
    
    # Query the database to get the list of cities
    cursor.execute("SELECT DISTINCT city FROM weatherdata")
    result = cursor.fetchall()
    
    cities = [row['city'] for row in result]
    
    return jsonify(cities)

@app.route('/get_current_weather', methods=['POST'])
def get_current_weather():
    data = request.data.decode('utf-8')
    city = extract_from_xml(data, 'city')
    
    if city:
        # Connect to the database
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME_2')
        )
        cursor = conn.cursor(dictionary=True)
        
        # Query the database to get the current weather for the city
        cursor.execute("SELECT temperature, humidity, heat_index FROM weatherdata WHERE city = %s", (city,))
        result = cursor.fetchone()
        print(result)
        if result:
            return jsonify(result)
        else:
            return jsonify({'status': 'failure'}), 400
    else:
        return jsonify({'status': 'failure'}), 400

@app.route('/get_forecast', methods=['POST'])
def get_forecast():
    data = request.data.decode('utf-8')
    city = extract_from_xml(data, 'city')
    
    if city:
        # Connect to the database
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME_2')
        )
        cursor = conn.cursor(dictionary=True)
        
        # Query the database to get the 7-day forecast for the city
        cursor.execute("""
            SELECT 
                hi_day_one, hi_level_day_one,
                hi_day_two, hi_level_day_two,
                hi_day_three, hi_level_day_three,
                hi_day_four, hi_level_day_four,
                hi_day_five, hi_level_day_five,
                hi_day_six, hi_level_day_six,
                hi_day_seven, hi_level_day_seven
            FROM weatherdataforecast 
            WHERE city = %s
        """, (city,))
        result = cursor.fetchone()
        
        if result:
            forecast = [
                {'day': 'Day 1', 'heat_index': result['hi_day_one'], 'condition': result['hi_level_day_one']},
                {'day': 'Day 2', 'heat_index': result['hi_day_two'], 'condition': result['hi_level_day_two']},
                {'day': 'Day 3', 'heat_index': result['hi_day_three'], 'condition': result['hi_level_day_three']},
                {'day': 'Day 4', 'heat_index': result['hi_day_four'], 'condition': result['hi_level_day_four']},
                {'day': 'Day 5', 'heat_index': result['hi_day_five'], 'condition': result['hi_level_day_five']},
                {'day': 'Day 6', 'heat_index': result['hi_day_six'], 'condition': result['hi_level_day_six']},
                {'day': 'Day 7', 'heat_index': result['hi_day_seven'], 'condition': result['hi_level_day_seven']}
            ]
            return jsonify(forecast)
        else:
            return jsonify({'status': 'failure'}), 400
    else:
        return jsonify({'status': 'failure'}), 400

def extract_from_xml(xml, tag):
    start = xml.find(f'<{tag}>') + len(f'<{tag}>')
    end = xml.find(f'</{tag}>')
    return xml[start:end]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)