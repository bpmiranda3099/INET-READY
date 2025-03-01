import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from loguru import logger

from hourly_heat_index import main as fetch_weather_data

def upload_to_firestore(results):
    """Upload weather data to Firestore"""
    # Path to service account key from environment or local file
    service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT', 'firebase_service_account.json')
    
    # Initialize the Firebase Admin SDK
    cred = credentials.Certificate(service_account_path)
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
