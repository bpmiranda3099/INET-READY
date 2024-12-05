from flask import Flask, request, jsonify
import os
import mysql.connector
from dotenv import load_dotenv
from flask_cors import CORS  # CORS handling

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    data = request.data.decode('utf-8')
    # Extract username and password from XML
    username = extract_from_xml(data, 'username')
    password = extract_from_xml(data, 'password')
    
    if username and password:
        # Connect to the database
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME_3')
        )
        cursor = conn.cursor(dictionary=True)
        # Query the database to check if the username exists and the password matches
        cursor.execute("SELECT user_id, password FROM user WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        if result and result['password'] == password:
            # Log the user activity
            user_id = result['user_id']
            activity_type = 'Login'
            activity_details = f'User {username} logged in successfully.'
            
            cursor.execute(
                "INSERT INTO UserActivityLog (user_id, activity_type, activity_details) VALUES (%s, %s, %s)",
                (user_id, activity_type, activity_details)
            )
            conn.commit()
            
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'failure'}), 400
            
    else:
        return jsonify({'status': 'failure'}), 400
        

def extract_from_xml(xml, tag):
    start = xml.find(f'<{tag}>') + len(f'<{tag}>')
    end = xml.find(f'</{tag}>')
    return xml[start:end]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)