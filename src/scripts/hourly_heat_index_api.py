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
        
        # Single collection for historical weather data
        weather_collection_ref = db.collection('hourly_weather_data')
        
        # Get current date and time for document IDs
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        current_time_id = current_time.replace(':', '-')
        
        # Create references to the simplified hierarchical structure:
        # Structure: hourly_weather_data (collection) -> date (doc) -> current_time_id (collection) -> city (doc)
        date_doc_ref = weather_collection_ref.document(current_date)
        time_collection_ref = date_doc_ref.collection(current_time_id)
        
        # Add a metadata document in the time collection
        metadata_ref = time_collection_ref.document('_metadata')
        metadata_ref.set({
            "time": current_time,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "cities_updated": [result['city'] for result in results]
        })
        
        # Store each city directly in the time collection
        for result in results:
            # Add cities directly to the time collection
            city_ref = time_collection_ref.document(result['city'])
            city_ref.set({
                "city": result['city'],
                "temperature": result['temperature'],
                "humidity": result['humidity'],
                "heat_index": result['heat_index'],
                "inet_level": result['inet_level'],
                "date_added": result['date_added'],
                "time_added": result['time_added'],
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Added data for {result['city']}")
        
        # Update the parent date document with metadata
        date_doc_ref.set({
            "date": current_date,
            "last_updated": current_time,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "update_count": firestore.Increment(1)  # Track how many updates happened on this date
        }, merge=True)
        
        logger.info(f"Successfully uploaded {len(results)} city records to Firestore")
        
        # Clean up Firebase connection
        firebase_admin.delete_app(firebase_admin.get_app())
        
        return f"{current_date}_{current_time_id}"
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
