import os
import time
import pandas as pd
import numpy as np
import xgboost as xgb
from datetime import timedelta, datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from loguru import logger
from functools import lru_cache
import multiprocessing
import concurrent.futures
import sys
from tqdm import tqdm, trange  # For progress bars

# Import validation functions from new modules
from validation import (
    perform_k_fold_cross_validation,
    perform_nested_cv_with_param_tuning,
    bootstrap_evaluation,
    perform_permutation_test,
    perform_time_based_validation,
    validate_model
)

# Get script directory for relative paths
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(script_dir, 'logs'), exist_ok=True)
log_file_path = os.path.join(script_dir, 'logs', 'predict_heat_index.log')

# Configure Loguru for both file and console logging
logger.remove()  # Remove default handlers
logger.add(log_file_path, rotation="10 MB", format="{time} | {level} | {message}", level="INFO")
# Keep technical logs only in the file, not in the console
logger.add(sys.stderr, format="<dim>{time:HH:mm:ss}</dim> | <level>{message}</level>", level="INFO", filter=lambda record: record.get("user_friendly", False))

# Set maximum number of threads for parallel processing
MAX_THREADS = max(4, multiprocessing.cpu_count() - 1)

def console_log(message, is_important=False, emoji=None):
    """Log user-friendly messages to console with formatting"""
    if emoji is None:
        emoji = "✨" if is_important else "➤"
    
    if is_important:
        tqdm.write(f"\n{emoji} {message} {emoji}")
    else:
        tqdm.write(f"{emoji} {message}")

@lru_cache(maxsize=32)
def load_data(file_path):
    try:
        logger.info(f"Loading data from {file_path}")
        data = pd.read_csv(file_path)
        logger.info(f"Data loaded successfully with {len(data)} rows")
        return data
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def check_required_columns(data, required_columns):
    try:
        if required_columns.issubset(data.columns):
            logger.info("CSV has all the required columns")
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
            # Make all dates timezone-naive
            data['Date'] = data['Date'].dt.tz_localize(None)
            data.sort_values(by=['City', 'Date'], inplace=True)
        else:
            missing_cols = required_columns - set(data.columns)
            logger.error(f"The CSV file must contain the following columns: {', '.join(missing_cols)}")
            raise KeyError(f"The CSV file must contain the following columns: {', '.join(missing_cols)}")
        return data
    except Exception as e:
        logger.error(f"Error checking required columns: {e}")
        raise

def prepare_data_for_regression(group):
    try:
        # Vectorized operation for better performance
        min_date = group['Date'].min()
        group['day'] = (group['Date'] - min_date).dt.days
        return group
    except Exception as e:
        logger.error(f"Error preparing data for regression: {e}")
        raise

def create_holdout_validation_set(data, test_size=0.1, random_state=42):
    """
    Create a completely separate holdout set that will only be used for final validation
    """
    try:
        logger.info("Creating holdout validation set")
        train_data, holdout_data = train_test_split(
            data, test_size=test_size, random_state=random_state
        )
        logger.info(f"Training set: {len(train_data)} samples, Holdout set: {len(holdout_data)} samples")
        return train_data, holdout_data
    except Exception as e:
        logger.error(f"Error creating holdout validation set: {e}")
        raise

def train_model(X_train, y_train, params=None):
    try:
        logger.info("Training the model")
        if params is None:
            # Add early stopping to prevent overfitting and improve speed
            model = xgb.XGBRegressor(
                objective='reg:squarederror',
                n_jobs=1,  # Single thread here as we'll parallelize at a higher level
                verbosity=0  # Reduce verbosity for speed
            )
        else:
            model = xgb.XGBRegressor(
                objective='reg:squarederror',
                n_jobs=1,
                verbosity=0,
                **params
            )
        
        # Use early stopping if validation data is provided
        model.fit(X_train, y_train)
        return model
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise

def make_predictions(model, group, date_range, features):
    try:
        future_days = np.array([(date - group['Date'].min()).days for date in date_range])
        future_X = pd.DataFrame(future_days, columns=['day'])
        
        # More efficient feature construction
        feature_means = {col: group[col].mean() for col in features[1:]}
        for col, val in feature_means.items():
            future_X[col] = val
            
        # Vectorized operations
        future_predictions = model.predict(future_X)
        variation_factors = np.random.uniform(0.95, 1.05, size=future_predictions.shape)
        varied_predictions = future_predictions * variation_factors
        return varied_predictions
    except Exception as e:
        logger.error(f"Error making predictions: {e}")
        raise

def calculate_metrics(y_test, y_pred, city):
    try:
        # Vectorized computations
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Log the results instead of saving to DB
        logger.info(f"Metrics for {city}:")
        logger.info(f"Mean Absolute Error (MAE): {mae}")
        logger.info(f"Mean Squared Error (MSE): {mse}")
        logger.info(f"R-squared (R²): {r2}")
        
        return {'city': city, 'mean_absolute_error': mae, 'mean_squared_error': mse, 'r_squared': r2}
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        raise

def calculate_initial_metrics(X_train, y_train, X_test, y_test, city):
    """Calculate metrics before validation/optimization with default model parameters"""
    try:
        logger.info(f"Calculating initial metrics for {city} with default parameters")
        # Train a model with default parameters but optimized for speed
        default_model = xgb.XGBRegressor(
            objective='reg:squarederror', 
            n_jobs=1,
            verbosity=0
        )
        default_model.fit(X_train, y_train)
        
        # Predict and calculate metrics
        y_pred = default_model.predict(X_test)
        
        return calculate_metrics(y_test, y_pred, f"{city} (Before Validation)")
    except Exception as e:
        logger.error(f"Error calculating initial metrics: {e}")
        raise

def save_predictions(predictions, file_path):
    try:
        logger.info(f"Saving predictions to {file_path}")
        predictions_df = pd.DataFrame(predictions)
        
        # Format the dates as YYYY-MM-DD
        if 'Date' in predictions_df.columns and pd.api.types.is_datetime64_any_dtype(predictions_df['Date']):
            predictions_df['Date'] = predictions_df['Date'].dt.strftime('%Y-%m-%d')
            logger.info("Formatted dates as YYYY-MM-DD")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Use efficient CSV writing
        predictions_df.to_csv(file_path, index=False, float_format='%.3f')
        logger.info("Predictions saved successfully")
    except Exception as e:
        logger.error(f"Error saving predictions: {e}")
        raise

def calculate_overall_prediction_rating(metrics_df):
    """
    Calculate an overall prediction rating based on all metrics across all cities
    Returns a score from 0-100 and a qualitative rating
    """
    try:
        logger.info("\n===== CALCULATING OVERALL PREDICTION RATING =====")
        
        # Extract metrics - use numpy arrays for efficiency
        mae_values = metrics_df['mean_absolute_error'].values
        mse_values = metrics_df['mean_squared_error'].values
        r2_values = metrics_df['r_squared'].values
        
        # Vectorized operations for better performance
        avg_mae = np.mean(mae_values)
        avg_mse = np.mean(mse_values)
        avg_r2 = np.mean(r2_values)
        
        logger.info(f"Average MAE across all cities: {avg_mae:.4f}")
        logger.info(f"Average MSE across all cities: {avg_mse:.4f}")
        logger.info(f"Average R² across all cities: {avg_r2:.4f}")
        
        # Normalize MAE and MSE to 0-1 scale (lower is better)
        # Using exponential decay function: exp(-metric/scaling_factor)
        mae_scaling = np.max([1.0, np.median(mae_values)])  # Adaptive scaling
        mse_scaling = np.max([1.0, np.median(mse_values)])  # Adaptive scaling
        
        norm_mae_score = np.exp(-avg_mae/mae_scaling)
        norm_mse_score = np.exp(-avg_mse/mse_scaling)
        
        # R² is already 0-1 scale (higher is better)
        r2_score_val = max(0, min(1, avg_r2))  # Clamp between 0 and 1
        
        # Calculate weighted overall score (0-1 scale)
        # Weights: 40% for R², 40% for MAE, 20% for MSE
        overall_score = (0.4 * r2_score_val) + (0.4 * norm_mae_score) + (0.2 * norm_mse_score)
        
        # Convert to 0-100 scale
        rating_score = overall_score * 100
        
        # Assign qualitative rating
        if rating_score >= 90:
            rating = "Excellent"
        elif rating_score >= 80:
            rating = "Very Good"
        elif rating_score >= 70:
            rating = "Good"
        elif rating_score >= 60:
            rating = "Fair"
        elif rating_score >= 50:
            rating = "Poor"
        else:
            rating = "Unreliable"
        
        logger.info(f"Normalized MAE Score: {norm_mae_score:.4f}")
        logger.info(f"Normalized MSE Score: {norm_mse_score:.4f}")
        logger.info(f"R² Score: {r2_score_val:.4f}")
        logger.info(f"Overall Prediction Score: {rating_score:.2f}/100")
        logger.info(f"Prediction Quality Rating: {rating}")
        
        return {
            'score': rating_score,
            'rating': rating,
            'avg_mae': float(avg_mae),  # Convert numpy types to native for JSON serialization
            'avg_mse': float(avg_mse),
            'avg_r2': float(avg_r2),
            'norm_mae_score': float(norm_mae_score),
            'norm_mse_score': float(norm_mse_score),
            'r2_score': float(r2_score_val)
        }
    except Exception as e:
        logger.error(f"Error calculating overall prediction rating: {e}")
        return {
            'score': 0,
            'rating': "Error in calculation",
            'avg_mae': 0,
            'avg_mse': 0,
            'avg_r2': 0
        }

def process_city_data(city_data):
    """Process data for a single city - extracted for parallel processing"""
    city, group = city_data
    try:
        # Use simplified, user-friendly messages
        tqdm.write(f"🏙️ Analyzing weather patterns for {city}")
        
        # Create progress bar for this city's processing steps
        with tqdm(total=6, desc=f"Working on {city}", leave=False, position=0) as pbar:
            group = prepare_data_for_regression(group)
            pbar.update(1)
            
            # Use the features available in the CSV
            features = ['day', 'Temperature Max', 'Temperature Min', 'Apparent Temperature Max', 
                       'Apparent Temperature Min', 'Wind Speed', 'Solar Radiation', 'Relative Humidity']
            
            # Create a holdout validation set (10% of data)
            train_data, holdout_data = create_holdout_validation_set(group, test_size=0.1)
            pbar.update(1)
            
            # Train and validate model using training data
            X_validation = train_data[features]
            y_validation = train_data['Heat Index']
            
            # Split validation data for before/after comparison
            X_train, X_test, y_train, y_test = train_test_split(
                X_validation, y_validation, test_size=0.2, random_state=42
            )
            pbar.update(1)
            
            # Calculate initial metrics with default model parameters
            before_metrics = calculate_initial_metrics(X_train, y_train, X_test, y_test, city)
            pbar.update(1)
            
            # Perform comprehensive model validation
            city_validation = validate_model(city, train_data, features)
            
            # Get the best parameters from nested CV
            best_params = city_validation['nested_cv']['best_params']
            pbar.update(1)
            
            # Train final model with best parameters
            model = train_model(X_train, y_train, best_params)
            
            # Make predictions for next 7 days
            start_date = datetime.now() + timedelta(days=1)
            date_range = [start_date + timedelta(days=i) for i in range(7)]
            varied_predictions = make_predictions(model, group, date_range, features)
            
            city_predictions = []
            for date, prediction in zip(date_range, varied_predictions):
                city_predictions.append({'City': city, 'Date': date, 'Predicted Heat Index': prediction})
            
            # Test on holdout set to get final metrics
            X_holdout = holdout_data[features]
            y_holdout = holdout_data['Heat Index']
            y_pred_holdout = model.predict(X_holdout)
            
            # Calculate metrics on holdout set
            holdout_metrics = calculate_metrics(y_holdout, y_pred_holdout, city)
            pbar.update(1)
            
            # Get predictions for the test set
            y_pred = model.predict(X_test)
            
            return {
                'city': city,
                'predictions': city_predictions,
                'metrics': holdout_metrics,
                'initial_metrics': before_metrics,
                'validation_results': city_validation
            }
    except Exception as e:
        tqdm.write(f"⚠️ Encountered an issue with {city}: {str(e).split(':')[0]}")
        return None

def log_predictions(predictions_df, metrics_df, initial_metrics_df):
    try:
        logger.info("Logging predictions and metrics comparison")
        logger.info("Predictions:")
        logger.info(predictions_df.head())
        logger.info("Metrics after validation:")
        logger.info(metrics_df.head())
        logger.info("Initial metrics before validation:")
        logger.info(initial_metrics_df.head())
    except Exception as e:
        logger.error(f"Error logging predictions and metrics: {e}")

def generate_forecast_json(predictions_df, overall_rating):
    """
    Generate a comprehensive JSON with predictions and rating information
    """
    try:
        forecast_data = {
            "generated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "forecast_period": "7 days",
            "overall_rating": {
                "score": float(overall_rating['score']),
                "rating": overall_rating['rating'],
                "stars": round(overall_rating['score'] / 20),
                "metrics": {
                    "avg_mae": float(overall_rating['avg_mae']),
                    "avg_mse": float(overall_rating['avg_mse']),
                    "avg_r2": float(overall_rating['avg_r2'])
                }
            },
            "cities": {}
        }
        
        # Group predictions by city
        cities = predictions_df['City'].unique()
        
        for city in cities:
            city_data = predictions_df[predictions_df['City'] == city]
            forecast_data["cities"][city] = []
            
            for _, row in city_data.iterrows():
                forecast_data["cities"][city].append({
                    "date": row['Date'],
                    "heat_index": float(row['Predicted Heat Index']),
                    "units": "°C"
                })
        
        return forecast_data
    except Exception as e:
        logger.error(f"Error generating forecast JSON: {e}")
        return {"error": "Failed to generate forecast data"}

def main():
    try:
        start_time = time.time()
        console_log("Starting heat index forecast preparation", True, "🌡️")
        
        # Display animated loading message
        with tqdm(total=100, desc="Getting ready", leave=True, position=0) as pbar:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Fix the file path format - remove the leading slash
            file_path = os.path.join(script_dir, '..', '..', 'public', 'data', 'historical_weather_data.csv')
            pbar.update(20)  # Show some progress
            
            # Simulate loading with animation
            for _ in range(5):
                time.sleep(0.05)  # Small delay for smoother animation
                pbar.update(5)
            
            data = load_data(file_path)
            pbar.update(25)
            
            # Update required columns to match the CSV structure
            required_columns = {'City', 'Date', 'Temperature Max', 'Temperature Min', 'Apparent Temperature Max', 
                              'Apparent Temperature Min', 'Wind Speed', 'Solar Radiation', 'Relative Humidity', 
                              'Heat Index'}
            
            # Rename 'City' column if it's actually named differently in the CSV
            if 'City' not in data.columns and 'city' in data.columns:
                data = data.rename(columns={'city': 'City'})
                
            pbar.update(10)
            
            data = check_required_columns(data, required_columns)
            pbar.update(15)
            
            # Group data by city once
            grouped = list(data.groupby('City'))
            pbar.update(20)
            
        console_log(f"Found weather data for {len(grouped)} cities", False, "🔍")
        console_log("Starting to analyze each city's weather patterns", False, "📊")
        
        # Progress bar for overall city processing
        with tqdm(total=len(grouped), desc="Analyzing cities", position=0) as main_pbar:
            # Use parallel processing for city data
            all_results = []
            completed_cities = 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                # Submit all tasks
                future_to_city = {executor.submit(process_city_data, city_group): city_group[0] 
                                for city_group in grouped}
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_city):
                    city = future_to_city[future]
                    try:
                        result = future.result()
                        if result:
                            all_results.append(result)
                            completed_cities += 1
                            main_pbar.update(1)
                            percent_complete = (completed_cities / len(grouped)) * 100
                            main_pbar.set_description(f"Analyzing cities - {percent_complete:.1f}% done")
                        else:
                            main_pbar.update(1)
                            tqdm.write(f"⚠️  Couldn't analyze {city}")
                    except Exception as e:
                        main_pbar.update(1)
                        tqdm.write(f"❌ Problem with {city}: {str(e).split(':')[0]}")
        
        # Collect all results
        console_log("Creating your forecasts", True, "📝")
        with tqdm(total=100, desc="Finalizing your report", position=0) as final_pbar:
            predictions = []
            metrics = []
            initial_metrics = []
            validation_results = []
            
            for result in all_results:
                if result:
                    predictions.extend(result['predictions'])
                    metrics.append(result['metrics'])
                    initial_metrics.append(result['initial_metrics'])
                    validation_results.append(result['validation_results'])
            
            final_pbar.update(20)
            
            date_today = datetime.now().strftime('%Y-%m-%d')
            
            # Modified output directory path to use public/data
            output_dir = os.path.join(script_dir, '..', '..', 'public', 'data', 'predicted_heat_index')
            os.makedirs(output_dir, exist_ok=True)
            
            final_pbar.update(10)
            save_predictions(predictions, os.path.join(output_dir, f'{date_today}_heat_index_prediction.csv'))
            final_pbar.update(15)
            
            # Save validation results
            validation_output = os.path.join(output_dir, f'{date_today}_model_validation_results.json')
            pd.DataFrame(validation_results).to_json(validation_output, orient='records')
            final_pbar.update(10)
            
            predictions_df = pd.DataFrame(predictions)
            # Format dates for the DataFrame if needed
            if 'Date' in predictions_df.columns and pd.api.types.is_datetime64_any_dtype(predictions_df['Date']):
                predictions_df['Date'] = predictions_df['Date'].dt.strftime('%Y-%m-%d')
                
            metrics_df = pd.DataFrame(metrics)
            initial_metrics_df = pd.DataFrame(initial_metrics)
            final_pbar.update(15)
            
            # Save metrics comparison
            metrics_comparison = os.path.join(output_dir, f'{date_today}_metrics_comparison.csv')
            initial_metrics_df.to_csv(metrics_comparison.replace('.csv', '_before.csv'), index=False)
            metrics_df.to_csv(metrics_comparison.replace('.csv', '_after.csv'), index=False)
            final_pbar.update(10)
            
            # Calculate and log overall prediction rating
            console_log("Checking forecast quality", False, "🔍")
            overall_rating = calculate_overall_prediction_rating(metrics_df)
            final_pbar.update(10)
            
            # Generate comprehensive forecast JSON
            console_log("Preparing forecast data", False, "🔄")
            forecast_json = generate_forecast_json(predictions_df, overall_rating)
            
            # Save forecast JSON
            forecast_file = os.path.join(output_dir, f'{date_today}_heat_index_forecast.json')
            with open(forecast_file, 'w') as f:
                import json
                json.dump(forecast_json, f, indent=4)
            console_log(f"Complete forecast saved to {forecast_file}", False, "💾")
            final_pbar.update(5)
            
            # Save overall rating to file (original format still maintained)
            rating_file = os.path.join(output_dir, f'{date_today}_overall_rating.json')
            with open(rating_file, 'w') as f:
                json.dump(overall_rating, f, indent=4)
            final_pbar.update(5)
            
            # Print sample output to console
            console_log("Sample forecast data:", False, "📊")
            
            # Show the first city as a sample
            sample_city = list(forecast_json["cities"].keys())[0]
            sample_data = {
                "overall_rating": forecast_json["overall_rating"],
                "sample_city": sample_city,
                "forecast": forecast_json["cities"][sample_city][:3]  # Show only first 3 days
            }
            
            # Print formatted JSON
            tqdm.write(json.dumps(sample_data, indent=2))
            
            # Add return statement to make the JSON data available to other code
            return forecast_json
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Print summary banner to console with simpler language
        console_log("=" * 60, True, "")
        console_log(f"HEAT INDEX FORECAST - {date_today}", True, "🌡️")
        console_log("=" * 60, True, "")
        console_log(f"Cities analyzed: {len(metrics_df)}")
        console_log(f"Forecast reliability score: {overall_rating['score']:.1f}/100")
        
        # Convert rating to simple stars
        stars = "★" * round(overall_rating['score'] / 20)
        stars += "☆" * (5 - round(overall_rating['score'] / 20))
        
        console_log(f"Quality rating: {stars} ({overall_rating['rating']})")
        console_log(f"All done in {int(elapsed_time/60)} minutes and {int(elapsed_time%60)} seconds")
        console_log("Forecast files saved successfully", False, "💾")
        console_log("=" * 60, True, "")
        
    except Exception as e:
        console_log(f"❌ Something went wrong: {str(e).split(':')[0]}", True)
        logger.error(f"Error in main process: {e}")

# Modified to return JSON when imported and called by other modules
if __name__ == "__main__":
    result = main()
else:
    # If imported as a module, provide a function to get forecast data
    def get_forecast_data(data_file=None):
        """
        Get heat index forecast data as JSON
        
        Parameters:
        data_file (str): Optional path to historical weather data CSV file
        
        Returns:
        dict: JSON-compatible dictionary with forecast data
        """
        return main()
