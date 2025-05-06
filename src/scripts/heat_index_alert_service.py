import os
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import messaging
from firebase_admin import exceptions as firebase_exceptions
from datetime import datetime, timedelta
from loguru import logger
import json

# Configure logger
logger.add("heat_index_alerts.log", rotation="1 day", retention="7 days", level="INFO")

class HeatIndexAlertService:
    """Service to detect significant heat index changes and send alerts to users"""
    
    def __init__(self):
        """Initialize the service"""
        self.db = None
        self.project_id = None
        self.initialize_firebase()
        
        # Configure thresholds for significant changes
        self.spike_threshold_percent = 15  # 15% increase is considered a spike
        self.drop_threshold_percent = -10  # 10% decrease is considered a significant drop
        
        # No longer using comparison window hours since we're comparing with previous entry
        # self.comparison_window_hours = 24  # Compare with data from 24 hours ago if available
    def initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            # Path to service account key from environment or local file
            service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT', 'firebase_service_account.json')
            
            # Load service account info for better error messages
            with open(service_account_path, 'r') as f:
                service_account = json.load(f)
                self.project_id = service_account.get('project_id')
                logger.info(f"Using Firebase project: {self.project_id}")
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            
            # Get Firestore client
            self.db = firestore.client()
            logger.info("Firebase initialized successfully")
            
        except firebase_exceptions.UnauthenticatedError as e:
            logger.error(f"Firebase authentication error: {e}")
            logger.error("Please check your service account credentials")
            raise
        except firebase_exceptions.PermissionDeniedError as e:
            logger.error(f"Firebase permission denied: {e}")
            logger.error("Please check that your service account has necessary permissions")
            raise
        except firebase_exceptions.NotFoundError as e:
            logger.error(f"Firebase resource not found: {e}")
            logger.error("Please check that the Firebase project exists")
            raise
        except firebase_exceptions.FirebaseError as e:
            logger.error(f"Firebase error ({e.code}): {e}")
            raise
        except Exception as e:
            logger.error(f"Firebase initialization error: {e}")
            raise
    def get_latest_data(self):
        """Get the most recent heat index data for all cities"""
        try:
            # Get all date documents, ordered by date descending
            weather_ref = self.db.collection('hourly_weather_data')
            date_docs = weather_ref.order_by('date', direction=firestore.Query.DESCENDING).limit(1).stream()
            
            latest_data = {}
            
            for date_doc in date_docs:
                date_id = date_doc.id
                date_data = date_doc.to_dict()
                
                # Get the latest time collection for this date
                time_collections = self.db.collection('hourly_weather_data').document(date_id).collections()
                time_ids = [time_col.id for time_col in time_collections if time_col.id != '_metadata']
                
                if time_ids:
                    # Get the most recent time
                    most_recent_time = sorted(time_ids)[-1]
                    
                    # Get city data from the most recent time
                    city_docs = self.db.collection('hourly_weather_data').document(date_id).collection(most_recent_time).stream()
                    
                    for doc in city_docs:
                        if doc.id != '_metadata':
                            city_data = doc.to_dict()
                            city_name = city_data.get('city')
                            
                            if city_name:
                                latest_data[city_name] = {
                                    'city': city_name,
                                    'heat_index': city_data.get('heat_index'),
                                    'inet_level': city_data.get('inet_level'),
                                    'temperature': city_data.get('temperature'),
                                    'humidity': city_data.get('humidity'),
                                    'time_added': city_data.get('time_added'),
                                    'date_added': city_data.get('date_added')
                                }
                    
                    logger.info(f"Loaded latest data from {date_id} {most_recent_time} for {len(latest_data)} cities")
                    break
            
            return latest_data
            
        except firebase_exceptions.NotFoundError as e:
            logger.error(f"Firebase document not found: {e}")
            return {}
        except firebase_exceptions.PermissionDeniedError as e:
            logger.error(f"Permission denied accessing Firestore data: {e}")
            return {}
        except firebase_exceptions.UnavailableError as e:
            logger.error(f"Firebase service unavailable: {e}")
            return {}
        except firebase_exceptions.FirebaseError as e:
            logger.error(f"Firebase error ({e.code}) getting latest data: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error getting latest data: {e}")
            return {}
    def get_comparison_data(self):
        """
        Get the immediately previous heat index data entry for comparison
        Returns dictionary of city data from the entry right before the most recent one
        """
        try:
            # First, identify the most recent entry (date and time)
            weather_ref = self.db.collection('hourly_weather_data')
            date_docs = weather_ref.order_by('date', direction=firestore.Query.DESCENDING).limit(2).stream()
            
            dates = []
            for date_doc in date_docs:
                dates.append(date_doc.id)
            
            if not dates:
                logger.error("No dates found in hourly_weather_data")
                return {}
            
            # Get the latest date's time collections
            latest_date = dates[0]
            latest_date_ref = weather_ref.document(latest_date)
            time_collections = latest_date_ref.collections()
            time_ids = [time_col.id for time_col in time_collections if time_col.id != '_metadata']
            
            if not time_ids:
                logger.error(f"No time collections found for date {latest_date}")
                return {}
            
            # Sort time collections to find the latest and second latest
            sorted_times = sorted(time_ids)
            
            # If we have at least 2 time entries on the latest date
            if len(sorted_times) >= 2:
                latest_time = sorted_times[-1]
                prev_time = sorted_times[-2]
                prev_date = latest_date
                logger.info(f"Found previous entry on same date: {prev_date} {prev_time}")
            
            # If we have only 1 time entry on the latest date, need to look at previous date
            elif len(dates) > 1:
                prev_date = dates[1]
                prev_date_ref = weather_ref.document(prev_date)
                prev_time_collections = prev_date_ref.collections()
                prev_time_ids = [time_col.id for time_col in prev_time_collections if time_col.id != '_metadata']
                
                if not prev_time_ids:
                    logger.error(f"No time collections found for previous date {prev_date}")
                    return {}
                    
                # Get the latest time from the previous date
                prev_time = sorted(prev_time_ids)[-1]
                logger.info(f"Found previous entry on previous date: {prev_date} {prev_time}")
            else:
                logger.error("Not enough historical data for comparison")
                return {}
            
            # Now fetch the city data from the previous entry
            comparison_data = {}
            city_docs = self.db.collection('hourly_weather_data').document(prev_date).collection(prev_time).stream()
            
            for doc in city_docs:
                if doc.id != '_metadata':
                    city_data = doc.to_dict()
                    city_name = city_data.get('city')
                    
                    if city_name:
                        comparison_data[city_name] = {
                            'city': city_name,
                            'heat_index': city_data.get('heat_index'),
                            'inet_level': city_data.get('inet_level'),
                            'temperature': city_data.get('temperature'),
                            'humidity': city_data.get('humidity'),
                            'time_added': city_data.get('time_added'),
                            'date_added': city_data.get('date_added')
                        }
            
            logger.info(f"Loaded comparison data from {prev_date} {prev_time} for {len(comparison_data)} cities")
            return comparison_data
            
        except firebase_exceptions.NotFoundError as e:
            logger.error(f"Firebase document not found in comparison data: {e}")
            return {}
        except firebase_exceptions.PermissionDeniedError as e:
            logger.error(f"Permission denied accessing Firestore comparison data: {e}")
            return {}
        except firebase_exceptions.UnavailableError as e:
            logger.error(f"Firebase service unavailable for comparison data: {e}")
            return {}
        except firebase_exceptions.FirebaseError as e:
            logger.error(f"Firebase error ({e.code}) getting comparison data: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error getting comparison data: {e}")
            return {}
    
    def _find_closest_time(self, time_ids, target_time):
        """Find the closest time to the target from a list of time IDs"""
        if not time_ids:
            return None
            
        # Sort times
        sorted_times = sorted(time_ids)
        
        # If target is earlier than all times, return the earliest
        if target_time < sorted_times[0]:
            return sorted_times[0]
            
        # If target is later than all times, return the latest
        if target_time > sorted_times[-1]:
            return sorted_times[-1]
            
        # Binary search for the closest time
        left, right = 0, len(sorted_times) - 1
        
        while left <= right:
            mid = (left + right) // 2
            
            if sorted_times[mid] == target_time:
                return sorted_times[mid]
            
            if sorted_times[mid] < target_time:
                left = mid + 1
            else:
                right = mid - 1
        
        # At this point, either left or right is the closest
        if left >= len(sorted_times):
            return sorted_times[right]
            
        if right < 0:
            return sorted_times[left]
            
        # Determine which is closer
        if abs(sorted_times[left].replace('-', '') - target_time.replace('-', '')) < abs(sorted_times[right].replace('-', '') - target_time.replace('-', '')):
            return sorted_times[left]
        else:
            return sorted_times[right]
    def detect_significant_changes(self, latest_data, comparison_data):
        """Detect significant changes in heat index"""
        significant_changes = []
        
        for city, current in latest_data.items():
            # Skip if we don't have comparison data for this city
            if city not in comparison_data:
                continue
                
            previous = comparison_data[city]
            
            # Skip if heat index data is missing
            if current.get('heat_index') is None or previous.get('heat_index') is None:
                continue
                
            current_heat_index = float(current['heat_index'])
            previous_heat_index = float(previous['heat_index'])
            
            # Skip if previous heat index is zero (to avoid division by zero)

            if previous_heat_index == 0:
                continue
                
            # Calculate percentage change
            percent_change = ((current_heat_index - previous_heat_index) / previous_heat_index) * 100
            
            # Log all heat index comparisons, regardless of significance
            logger.info(f"Heat Index Comparison - {city}: {previous_heat_index} → {current_heat_index} ({percent_change:.1f}%)")
            
            change_type = None
            if percent_change >= self.spike_threshold_percent:
                change_type = 'spike'
            elif percent_change <= self.drop_threshold_percent:
                change_type = 'drop'
                
            if change_type:
                significant_changes.append({
                    'city': city,
                    'current_heat_index': current_heat_index,
                    'previous_heat_index': previous_heat_index,
                    'percent_change': round(percent_change, 1),
                    'change_type': change_type,
                    'inet_level': current.get('inet_level'),
                    'temperature': current.get('temperature'),
                    'humidity': current.get('humidity'),
                    'timestamp': datetime.now().isoformat()
                })
                logger.info(f"Detected {change_type} in {city}: {previous_heat_index} → {current_heat_index} ({percent_change:.1f}%)")
        
        return significant_changes
    def get_users_in_cities(self, city_names):
        """Get users in the specified cities who have enabled notifications"""
        try:
            city_user_tokens = {}
            
            # Get all users with notifications enabled
            users_ref = self.db.collection('users')
            users = users_ref.where('notification_enabled', '==', True).stream()
            
            for user_doc in users:
                user_data = user_doc.to_dict()
                
                # Check if user has location and FCM token
                if 'location' in user_data and 'fcm_token' in user_data:
                    user_city = user_data['location'].get('city')
                    fcm_token = user_data['fcm_token']
                    
                    # If user is in one of the affected cities
                    if user_city in city_names and fcm_token:
                        if user_city not in city_user_tokens:
                            city_user_tokens[user_city] = []
                            
                        # Add token to the city's list
                        city_user_tokens[user_city].append(fcm_token)
            
            # Count users by city
            for city, tokens in city_user_tokens.items():
                logger.info(f"Found {len(tokens)} users in {city} with notifications enabled")
                
            return city_user_tokens
            
        except firebase_exceptions.NotFoundError as e:
            logger.error(f"Firebase users collection not found: {e}")
            return {}
        except firebase_exceptions.PermissionDeniedError as e:
            logger.error(f"Permission denied accessing users data: {e}")
            return {}
        except firebase_exceptions.UnavailableError as e:
            logger.error(f"Firebase service unavailable when fetching users: {e}")
            return {}
        except firebase_exceptions.FirebaseError as e:
            logger.error(f"Firebase error ({e.code}) getting users in cities: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error getting users in cities: {e}")
            return {}
    def send_notifications(self, significant_changes, city_user_tokens):
        """Send notifications to users in affected cities"""
        if not significant_changes:
            logger.info("No significant changes detected. No notifications sent.")
            return {'success': True, 'notifications_sent': 0}
            
        if not city_user_tokens:
            logger.info("No users found in affected cities. No notifications sent.")
            return {'success': True, 'notifications_sent': 0}
            
        results = {
            'success': True,
            'notifications_sent': 0,
            'failures': 0,
            'cities': {}
        }
        
        try:
            for change in significant_changes:
                city = change['city']
                
                # Skip if no users in this city
                if city not in city_user_tokens or not city_user_tokens[city]:
                    continue
                    
                tokens = city_user_tokens[city]
                
                # Prepare notification based on change type
                if change['change_type'] == 'spike':
                    title = f"Heat Index Alert for {city}"
                    body = f"Heat index has increased by {change['percent_change']}% to {change['current_heat_index']}°C (INET Level: {change['inet_level']}). Stay indoors and always hydrate!"
                else:  # drop
                    title = f"Heat Index Update for {city}"
                    body = f"Heat index has decreased by {abs(change['percent_change'])}% to {change['current_heat_index']}°C (INET Level: {change['inet_level']})."
                
                # Additional data for the notification
                data = {
                    'type': 'HEAT_INDEX_ALERT',
                    'change_type': change['change_type'],
                    'city': city,
                    'current_heat_index': str(change['current_heat_index']),
                    'previous_heat_index': str(change['previous_heat_index']),
                    'percent_change': str(change['percent_change']),
                    'inet_level': str(change['inet_level']),
                    'timestamp': change['timestamp']
                }
                
                # Create and send the message
                message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    data=data,
                    tokens=tokens
                )
                
                # Send the message
                response = messaging.send_multicast(message)
                
                # Record results
                city_result = {
                    'success_count': response.success_count,
                    'failure_count': response.failure_count,
                    'tokens_count': len(tokens),
                    'notification_title': title,
                    'notification_body': body
                }
                
                results['notifications_sent'] += response.success_count
                results['failures'] += response.failure_count
                results['cities'][city] = city_result
                
                logger.info(f"Sent {response.success_count} notifications to users in {city} ({response.failure_count} failures)")
            
            # Log a summary
            logger.info(f"Notification summary: {results['notifications_sent']} sent, {results['failures']} failed")
            
            # Record notification history in Firestore
            self._record_notification_history(significant_changes, results)
            
            return results
            
        except firebase_exceptions.InvalidArgumentError as e:
            logger.error(f"Invalid notification data: {e}")
            return {'success': False, 'error': str(e)}
        except firebase_exceptions.UnauthenticatedError as e:
            logger.error(f"Firebase authentication error while sending notifications: {e}")
            return {'success': False, 'error': str(e)}
        except firebase_exceptions.UnavailableError as e:
            logger.error(f"Firebase messaging service unavailable: {e}")
            return {'success': False, 'error': str(e)}
        except firebase_exceptions.InternalError as e:
            logger.error(f"Firebase internal error while sending notifications: {e}")
            return {'success': False, 'error': str(e)}
        except firebase_exceptions.FirebaseError as e:
            logger.error(f"Firebase error ({e.code}) sending notifications: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
            return {'success': False, 'error': str(e)}
    def _record_notification_history(self, changes, results):
        """Record notification history in Firestore"""
        try:
            # Create a document in the notification_history collection
            history_ref = self.db.collection('notification_history').document()
            
            history_ref.set({
                'timestamp': firestore.SERVER_TIMESTAMP,
                'date': datetime.now().strftime("%Y-%m-%d"),
                'time': datetime.now().strftime("%H:%M:%S"),
                'changes': changes,
                'results': results
            })
            
            logger.info("Recorded notification history in Firestore")
            
        except firebase_exceptions.PermissionDeniedError as e:
            logger.error(f"Permission denied recording notification history: {e}")
        except firebase_exceptions.UnavailableError as e:
            logger.error(f"Firebase service unavailable while recording history: {e}")
        except firebase_exceptions.DeadlineExceededError as e:
            logger.error(f"Deadline exceeded when recording notification history: {e}")
        except firebase_exceptions.FirebaseError as e:
            logger.error(f"Firebase error ({e.code}) recording notification history: {e}")
        except Exception as e:
            logger.error(f"Error recording notification history: {e}")
    def run(self):
        """Run the heat index alert service"""
        try:
            logger.info("Starting Heat Index Alert Service")
            
            # Get the latest data
            latest_data = self.get_latest_data()
            if not latest_data:
                logger.error("No latest data found. Exiting.")
                return False
                
            # Get immediately previous entry data for comparison
            comparison_data = self.get_comparison_data()
            if not comparison_data:
                logger.error("No comparison data found. Exiting.")
                return False
                
            # Detect significant changes
            significant_changes = self.detect_significant_changes(latest_data, comparison_data)
            
            if significant_changes:
                logger.info(f"Detected {len(significant_changes)} significant heat index changes")
                
                # Get affected cities
                affected_cities = [change['city'] for change in significant_changes]
                
                # Get users in affected cities
                city_user_tokens = self.get_users_in_cities(affected_cities)
                
                # Send notifications
                results = self.send_notifications(significant_changes, city_user_tokens)
                
                return results['success']
            else:
                logger.info("No significant heat index changes detected")
                return True
                
        except firebase_exceptions.UnavailableError as e:
            logger.error(f"Firebase service unavailable during service run: {e}")
            return False
        except firebase_exceptions.FirebaseError as e:
            logger.error(f"Firebase error ({e.code}) running heat index alert service: {e}")
            return False
        except Exception as e:
            logger.error(f"Error running heat index alert service: {e}")
            return False
        finally:
            # Clean up Firebase connection
            try:
                if firebase_admin._apps:
                    firebase_admin.delete_app(firebase_admin.get_app())
                    logger.info("Firebase connection closed")
            except firebase_exceptions.FirebaseError as e:
                logger.error(f"Firebase error ({e.code}) closing Firebase connection: {e}")
            except Exception as e:
                logger.error(f"Error closing Firebase connection: {e}")

def main():
    """Main entry point for the script"""
    start_time = time.time()
    
    # Add a delay to ensure the hourly data update is complete
    delay_seconds = int(os.environ.get('ALERT_DELAY_SECONDS', 60))
    logger.info(f"Waiting {delay_seconds} seconds to ensure data update is complete...")
    time.sleep(delay_seconds)
    
    service = HeatIndexAlertService()
    success = service.run()
    
    end_time = time.time()
    logger.info(f"Heat Index Alert Service completed in {end_time - start_time:.2f} seconds")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
