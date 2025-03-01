import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from loguru import logger

from hourly_heat_index import main as fetch_weather_data

def upload_to_firestore(results):
    """Upload weather data to Firestore"""
    try:
        # Path to service account key from environment or local file
        service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT', 'firebase_service_account.json')
        
        # Debug the service account to identify project issues
        try:
            with open(service_account_path, 'r') as f:
                import json
                service_account = json.load(f)
                project_id = service_account.get('project_id')
                logger.info(f"Using Firebase project: {project_id}")
                
                # Check if this matches your web app's project
                logger.info(f"⚠️ Verify this matches your web app's Firebase project ID")
                logger.info(f"⚠️ Ensure you've created a Firestore database at: https://console.firebase.google.com/project/{project_id}/firestore")
        except Exception as e:
            logger.error(f"Could not read service account file: {e}")
        
        # Initialize the Firebase Admin SDK
        cred = credentials.Certificate(service_account_path)
        # Extract project ID for better error messages
        project_id = cred.project_id
        logger.info(f"Connecting to Firebase project: {project_id}")
        
        firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        collection_ref = db.collection('latest_hourly_heat_index')
        
        # Store each city directly in the collection
        for result in results:
            # Use the city name as the document ID
            city_doc = collection_ref.document(result['city'])
            city_doc.set({
                "city": result['city'],
                "temperature": result['temperature'],
                "humidity": result['humidity'],
                "heat_index": result['heat_index'],
                "inet_level": result['inet_level'],
                "date_added": result['date_added'],
                "time_added": result['time_added']
            })
            logger.info(f"Added data for {result['city']}")
        
        logger.info(f"Successfully uploaded {len(results)} city records to Firestore")
        
        # Clean up Firebase connection
        firebase_admin.delete_app(firebase_admin.get_app())
        
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    except Exception as e:
        if "database (default) does not exist" in str(e):
            logger.error(f"Firebase Firestore database doesn't exist! You need to create it in the Firebase console: https://console.firebase.google.com/project/{cred.project_id}/firestore")
            logger.error("Steps to create database: 1) Go to Firebase Console 2) Select your project 3) Click 'Firestore Database' 4) Click 'Create database' 5) Start in production mode 6) Choose a location")
        else:
            logger.error(f"Firebase error: {e}")
        raise

def main():
    """Main function to run in GitHub Actions"""
    try:
        # Get weather data
        results = fetch_weather_data()
        
        # Upload to Firestore
        batch_id = upload_to_firestore(results)
        
        print(f"Data uploaded successfully. Batch ID: {batch_id}")
        return results
    except Exception as e:
        logger.error(f"Error in GitHub Actions trigger: {e}")
        raise e

if __name__ == "__main__":
    main()
