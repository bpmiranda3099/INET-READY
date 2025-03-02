#!/usr/bin/env python3
"""
Daily Weather Insights - Generate weather insights and travel tips
using Gemini API and send push notifications to users.
"""
import os
import sys
import json
import time
import argparse
import tempfile
import subprocess
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore, messaging

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(script_dir))

# Constants
DEFAULT_FCM_TOPIC = "daily_weather_insights"
MAX_NOTIFICATION_LENGTH = 180  # Characters for the notification preview
NODE_BRIDGE_SCRIPT = os.path.join(script_dir, "generate_weather_insights.js")

# Get Firebase credentials path from environment variable or use default
FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_SERVICE_ACCOUNT', os.path.join(
    os.path.dirname(os.path.dirname(script_dir)),  # Go up to project root
    'config', 
    'firebase-credentials.json'
))

# For environment variables needed by Node.js
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY

def initialize_firebase():
    """
    Initialize Firebase connection
    
    Returns:
    tuple: (firestore.Client, messaging.Client) or (None, None) if connection failed
    """
    try:
        if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
            print(f"Firebase credentials file not found at {FIREBASE_CREDENTIALS_PATH}")
            
            # Check for common CI paths when running in GitHub Actions
            ci_paths = [
                './firebase_service_account.json',  # Root level in GitHub Actions
                '../firebase_service_account.json',  # One level up
                '../../firebase_service_account.json',  # Two levels up
            ]
            
            found_path = None
            for path in ci_paths:
                if os.path.exists(path):
                    found_path = path
                    break
                    
            if found_path:
                print(f"Found Firebase credentials at alternate path: {found_path}")
                cred = credentials.Certificate(found_path)
            else:
                print("Could not locate Firebase credentials file")
                return None, None
        else:
            # Use the original path
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            
        if not firebase_admin._apps:  # Check if already initialized
            firebase_admin.initialize_app(cred)
        
        # Get Firestore and Messaging clients
        db = firestore.client()
        fcm = messaging
        print("Firebase connection established successfully")
        return db, fcm
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None, None

def get_latest_heat_index_forecast(db):
    """
    Get the latest heat index forecast from Firestore
    
    Parameters:
    db (firestore.Client): Firestore database client
    
    Returns:
    dict: Latest forecast data or None if not found
    """
    try:
        # Get the heat index forecast collection
        heat_index_ref = db.collection('heat_index_forecast')
        
        # Query for the most recent document
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Try to get today's forecast first
        forecast_doc = heat_index_ref.document(today).get()
        
        # If not found, try yesterday's
        if not forecast_doc.exists:
            forecast_doc = heat_index_ref.document(yesterday).get()
        
        if not forecast_doc.exists:
            # Fall back to getting the most recent document
            docs = heat_index_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).get()
            docs_list = list(docs)
            if not docs_list:
                print("No forecast documents found in Firestore")
                return None
            forecast_doc = docs_list[0]
        
        # Get the base forecast data
        forecast_data = forecast_doc.to_dict()
        if not forecast_data:
            print("Forecast document exists but contains no data")
            return None
        
        # Get city-specific forecasts from the subcollection
        cities_data = {}
        cities_ref = forecast_doc.reference.collection('cities')
        city_docs = cities_ref.get()
        
        for city_doc in city_docs:
            city_data = city_doc.to_dict()
            if city_data and 'city' in city_data and 'forecast' in city_data:
                cities_data[city_data['city']] = city_data['forecast']
        
        # Add cities data to the main forecast
        forecast_data['cities'] = cities_data
        
        return forecast_data
    except Exception as e:
        print(f"Error retrieving forecast data: {e}")
        return None

def call_gemini_via_node_bridge(forecast_data):
    """
    Call the Gemini API to generate insights from forecast data via Node.js bridge
    
    Parameters:
    forecast_data (dict): Heat index forecast data
    
    Returns:
    str: Generated insights or None if failed
    """
    try:
        # Create a temporary file for the forecast data
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as temp_input:
            json.dump(forecast_data, temp_input)
            temp_input_path = temp_input.name
            
        # Create a temporary file for the output
        temp_output = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_output_path = temp_output.name
        temp_output.close()  # Close before passing to subprocess
            
        print(f"Using Node bridge script at: {NODE_BRIDGE_SCRIPT}")
        
        # Check if Node.js bridge script exists
        if not os.path.exists(NODE_BRIDGE_SCRIPT):
            print(f"Error: Node bridge script not found at {NODE_BRIDGE_SCRIPT}")
            return None
            
        # Call the Node.js bridge script
        try:
            result = subprocess.run(
                ["node", NODE_BRIDGE_SCRIPT, temp_input_path, temp_output_path],
                capture_output=True,
                text=True,
                check=True,
                env={**os.environ}
            )
            
            # Read the output from the temporary file
            with open(temp_output_path, 'r') as f:
                insights = f.read()
                
            return insights
        except subprocess.CalledProcessError as e:
            print(f"Error running Node.js bridge: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return None
    except Exception as e:
        print(f"Error in call_gemini_via_node_bridge: {e}")
        return None
    finally:
        # Clean up temporary files
        if 'temp_input_path' in locals() and os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
        if 'temp_output_path' in locals() and os.path.exists(temp_output_path):
            os.unlink(temp_output_path)

def create_push_notification(insights):
    """
    Create push notification content from insights
    
    Parameters:
    insights (str): Generated insights from Gemini
    
    Returns:
    tuple: (title, body, data) for the notification
    """
    if not insights:
        return None, None, None
        
    # Extract title from the TODAY'S SUMMARY section
    title = "Daily Weather Insights"
    
    # Find and extract the summary section
    summary_match = None
    if "TODAY'S SUMMARY:" in insights:
        summary_parts = insights.split("TODAY'S SUMMARY:")
        if len(summary_parts) > 1:
            summary_line = summary_parts[1].strip().split("\n")[0].strip()
            if summary_line:
                title = summary_line
                if len(title) > 50:  # Truncate if too long
                    title = title[:47] + "..."
    
    # Create preview text (truncated if needed)
    preview = insights[:MAX_NOTIFICATION_LENGTH]
    if len(insights) > MAX_NOTIFICATION_LENGTH:
        preview = preview[:preview.rfind(" ")] + "..."
    
    # Create notification structure
    notification = {
        'title': title,
        'body': preview
    }
    
    # Additional data to include with the notification
    data = {
        'full_insights': insights,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'type': 'daily_weather_insights'
    }
    
    return notification, data

def send_push_notifications(fcm, notification, data, topic=DEFAULT_FCM_TOPIC):
    """
    Send push notifications to users subscribed to a topic
    
    Parameters:
    fcm (messaging): Firebase Cloud Messaging client
    notification (dict): Notification content
    data (dict): Additional data to send
    topic (str): Topic to send to
    
    Returns:
    bool: True if successful, False otherwise
    """
    try:
        # Convert all data values to strings as required by FCM
        string_data = {k: str(v) for k, v in data.items()}
        
        # Create message
        message = messaging.Message(
            notification=messaging.Notification(
                title=notification['title'],
                body=notification['body'],
            ),
            data=string_data,
            topic=topic,
        )
        
        # Send message
        response = fcm.send(message)
        print(f"Successfully sent notification: {response}")
        return True
    except Exception as e:
        print(f"Error sending push notification: {e}")
        return False

def store_insights_in_firestore(db, insights):
    """
    Store generated insights in Firestore for historical reference
    
    Parameters:
    db (firestore.Client): Firestore database client
    insights (str): Generated insights text
    
    Returns:
    bool: True if successful, False otherwise
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Save to insights collection
        insights_ref = db.collection('weather_insights')
        insights_ref.document(today).set({
            'insights': insights,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'date': today
        })
        
        print(f"Successfully stored insights in Firestore for date: {today}")
        return True
    except Exception as e:
        print(f"Error storing insights in Firestore: {e}")
        return False

def check_node_installation():
    """
    Check if Node.js is installed and available
    
    Returns:
    bool: True if Node.js is installed, False otherwise
    """
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Generate daily weather insights and send push notifications'
    )
    parser.add_argument('--dry-run', action='store_true', 
                      help='Generate insights without sending notifications')
    parser.add_argument('--topic', default=DEFAULT_FCM_TOPIC,
                      help=f'FCM topic to send notifications to (default: {DEFAULT_FCM_TOPIC})')
    args = parser.parse_args()
    
    # Check if Node.js is installed
    if not check_node_installation():
        print("Error: Node.js is required but not found in PATH")
        return 1
    
    # Initialize Firebase
    db, fcm = initialize_firebase()
    if not db:
        print("Failed to initialize Firebase")
        return 1
    
    # Get latest heat index forecast
    forecast_data = get_latest_heat_index_forecast(db)
    if not forecast_data:
        print("No forecast data available")
        return 1
    
    # Generate insights using Gemini API via Node.js bridge
    insights = call_gemini_via_node_bridge(forecast_data)
    if not insights:
        print("Failed to generate insights")
        return 1
    
    print("\n===== Generated Weather Insights =====")
    print(insights)
    print("======================================\n")
    
    # Store insights in Firestore
    store_insights_in_firestore(db, insights)
    
    # Create push notification content
    notification, data = create_push_notification(insights)
    
    # Send push notification if not in dry-run mode
    if not args.dry_run:
        if send_push_notifications(fcm, notification, data, args.topic):
            print(f"Successfully sent push notification to topic: {args.topic}")
        else:
            print("Failed to send push notification")
            return 1
    else:
        print("Dry run mode: notification not sent")
        print(f"Notification title: {notification['title']}")
        print(f"Notification body: {notification['body']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
