#!/usr/bin/env python3
"""
Heat Index Forecast Tool - Combined API and CLI interface

This module provides both programmatic API access to heat index forecasts
and a command-line interface for retrieving and displaying forecasts.
"""
import json
import os
import sys
import argparse
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Add the parent directory to sys.path so we can import predict_heat_index
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    # Import the main prediction module
    from predict_heat_index import get_forecast_data
except ImportError:
    print("Error: Could not import prediction module")
    sys.exit(1)

# Get Firebase credentials path from environment variable or use default
FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_SERVICE_ACCOUNT', os.path.join(
    os.path.dirname(os.path.dirname(script_dir)),  # Go up to project root
    'config', 
    'firebase-credentials.json'
))

# ======= Firebase Functions =======

def initialize_firebase():
    """
    Initialize Firebase connection
    
    Returns:
    firestore.Client: Firestore client or None if connection failed
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
                return None
        else:
            # Use the original path
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            
        if not firebase_admin._apps:  # Check if already initialized
            firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        print("Firebase connection established successfully")
        return db
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None

def send_forecast_to_firebase(forecast_data):
    """
    Send heat index forecast data to Firebase
    
    Parameters:
    forecast_data (dict): Forecast data to send
    
    Returns:
    bool: True if successful, False otherwise
    """
    try:
        db = initialize_firebase()
        if not db:
            print("Failed to initialize Firebase")
            return False
            
        # Create a collection reference
        heat_index_ref = db.collection('heat_index_forecast')
        
        # Add timestamp to the data
        forecast_data['timestamp'] = firestore.SERVER_TIMESTAMP
        
        # Add the generated date as the document ID
        generated_date = forecast_data.get('generated_on', datetime.now().strftime("%Y-%m-%d"))
        generated_date = generated_date.split()[0]  # Extract just the date part
        
        # Store the overall forecast data
        heat_index_ref.document(generated_date).set({
            'generated_on': forecast_data['generated_on'],
            'forecast_period': forecast_data['forecast_period'],
            'overall_rating': forecast_data['overall_rating'],
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        # Store individual city forecasts
        cities_ref = heat_index_ref.document(generated_date).collection('cities')
        for city, forecast in forecast_data['cities'].items():
            cities_ref.document(city).set({
                'city': city,
                'forecast': forecast,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            
        print(f"Forecast data successfully sent to Firebase for date: {generated_date}")
        return True
    except Exception as e:
        print(f"Error sending forecast to Firebase: {e}")
        return False

# ======= API Functions =======

def get_latest_forecast():
    """
    Generate a new heat index forecast
    
    Returns:
    dict: JSON-compatible dictionary with forecast data
    """
    forecast = get_forecast_data()
    
    # Send to Firebase if forecast was generated successfully
    if forecast and 'overall_rating' in forecast:
        send_forecast_to_firebase(forecast)
        
    return forecast

def get_forecast_from_file():
    """
    Get the most recent forecast from saved JSON files
    
    Returns:
    dict: JSON-compatible dictionary with forecast data, or None if no files found
    """
    try:
        # Find the latest forecast file
        data_dir = os.path.join(script_dir, 'data', 'predicted_heat_index')
        if not os.path.exists(data_dir):
            print(f"Data directory not found: {data_dir}")
            return None
            
        # List all forecast JSON files
        json_files = [f for f in os.listdir(data_dir) if f.endswith('_heat_index_forecast.json')]
        
        if not json_files:
            print("No forecast files found")
            return None
            
        # Sort by date (files are named YYYY-MM-DD_heat_index_forecast.json)
        latest_file = sorted(json_files)[-1]
        
        # Load and return the JSON data
        with open(os.path.join(data_dir, latest_file), 'r') as f:
            forecast_data = json.load(f)
        
        return forecast_data
    except Exception as e:
        print(f"Error loading forecast data: {e}")
        return None

def filter_cities(data, city_pattern):
    """
    Filter forecast data to only include cities matching the provided pattern
    
    Parameters:
    data (dict): Forecast data dictionary
    city_pattern (str): Pattern to match against city names
    
    Returns:
    dict: Filtered forecast data
    """
    if 'cities' not in data:
        return data
        
    pattern = city_pattern.lower()
    filtered_cities = {}
    
    for city, forecast in data['cities'].items():
        if pattern in city.lower():
            filtered_cities[city] = forecast
    
    if not filtered_cities:
        return None
        
    # Create a copy of the original data with filtered cities
    filtered_data = data.copy()
    filtered_data['cities'] = filtered_cities
    return filtered_data


# ======= CLI Functions =======

def display_forecast(data, json_output=False):
    """
    Display the forecast data in a human-readable format or as JSON
    
    Parameters:
    data (dict): Forecast data dictionary
    json_output (bool): If True, output in JSON format
    """
    if json_output:
        print(json.dumps(data, indent=2))
        return
        
    print("\n===== HEAT INDEX FORECAST =====")
    print(f"Generated on: {data.get('generated_on', 'unknown')}")
    print(f"Forecast period: {data.get('forecast_period', '7 days')}")
    print(f"Overall rating: {data['overall_rating']['rating']} ({data['overall_rating']['score']:.1f}/100)")
    
    # Print star rating
    stars = "★" * data['overall_rating']['stars'] + "☆" * (5 - data['overall_rating']['stars'])
    print(f"Quality: {stars}")
    
    if 'cities' in data:
        print("\nForecast by City:")
        for city, forecast in data['cities'].items():
            print(f"\n{city}:")
            for day in forecast:
                print(f"  {day['date']}: {day['heat_index']:.1f}{day['units']}")
    else:
        print("\nNo city forecast data available")


def main():
    """CLI interface for heat index forecast tool"""
    parser = argparse.ArgumentParser(
        description='Heat Index Forecast Tool',
        epilog='Example: heat_index_forecast_api.py --city "New York" --json'
    )
    parser.add_argument('--city', help='Filter results by city name (case-insensitive)')
    parser.add_argument('--regenerate', action='store_true', help='Force regeneration of forecast')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--save', help='Save output to specified file')
    parser.add_argument('--firebase', action='store_true', help='Send data to Firebase')
    args = parser.parse_args()
    
    # Get forecast data
    if args.regenerate:
        print("Regenerating forecast data...")
        data = get_latest_forecast()  # This already sends to Firebase
    else:
        data = get_forecast_from_file()
        if not data:
            print("No existing forecast found. Generating new forecast...")
            data = get_latest_forecast()  # This already sends to Firebase
        elif args.firebase:
            # Explicitly send to Firebase if requested
            send_forecast_to_firebase(data)
    
    if not data:
        print("Error: Could not retrieve forecast data")
        return 1
    
    # Filter by city if requested
    if args.city:
        filtered_data = filter_cities(data, args.city)
        if not filtered_data:
            print(f"No cities found matching '{args.city}'")
            return 1
        data = filtered_data
    
    # Display the forecast
    display_forecast(data, args.json)
    
    # Save to file if requested
    if args.save:
        try:
            with open(args.save, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\nForecast saved to {args.save}")
        except Exception as e:
            print(f"Error saving to file: {e}")
            return 1
    
    return 0


# ======= Script execution =======

if __name__ == "__main__":
    sys.exit(main())
else:
    # When imported as a module, provide a simple usage example
    print(f"Imported {__name__}. Use get_latest_forecast() or get_forecast_from_file() to access forecasts.")
