import os
import time
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import matplotlib.pyplot as plt
import mysql.connector
from datetime import timedelta, datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from loguru import logger
from dotenv import load_dotenv
from functools import lru_cache

root_dir = os.path.dirname(os.path.abspath(__file__))
parent_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

log_file_path = os.path.join(root_dir, 'logs', 'predict_heat_index.log')
logger.remove()
logger.add(log_file_path, rotation="10 MB")

@lru_cache(maxsize=32)
def load_data(file_path):
    try:
        logger.info("Loading the data")
        data = pd.read_csv(file_path, encoding='latin1')
        logger.info("Removing the first row which seems to be corrupted")
        data = data.drop(index=0)
        return data
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def check_required_columns(data, required_columns):
    try:
        if required_columns.issubset(data.columns):
            logger.info("CSV has all the required columns")
            data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d %H:%M:%S%z') 
            data = data.sort_values(by=['Place', 'Date'])
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
        group['day'] = (group['Date'] - group['Date'].min()).dt.days
        group['Date'] = group['Date'].apply(lambda x: x.replace(tzinfo=None) if x.tzinfo else x)
        return group
    except Exception as e:
        logger.error(f"Error preparing data for regression: {e}")
        raise

def train_model(X_train, y_train):
    try:
        logger.info("Training the model")
        model = xgb.XGBRegressor(objective='reg:squarederror')
        model.fit(X_train, y_train)
        return model
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise

def make_predictions(model, group, date_range, features):
    try:
        future_days = [(date - group['Date'].min()).days for date in date_range]
        future_X = pd.DataFrame(future_days, columns=['day'])
        future_X = future_X.assign(**{col: group[col].mean() for col in features[1:]})
        future_predictions = model.predict(future_X)
        variation_factors = np.random.uniform(0.95, 1.05, size=future_predictions.shape)
        varied_predictions = future_predictions * variation_factors
        return varied_predictions
    except Exception as e:
        logger.error(f"Error making predictions: {e}")
        raise

def plot_actual_vs_predicted(X_test, y_test, y_pred, place):
    try:
        plt.figure(figsize=(10, 6))
        plt.scatter(X_test['day'], y_test, color='blue', label='Actual Heat Index')
        plt.scatter(X_test['day'], y_pred, color='red', label='Predicted Heat Index')
        plt.xlabel('Day')
        plt.ylabel('Heat Index')
        plt.title(f'Actual vs Predicted Heat Index for {place}')
        plt.legend()
        date_today = datetime.now().strftime('%Y-%m-%d')
        output_dir = os.path.join(root_dir, 'charts', 'heat_index_comparison', date_today)
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, f'{place}_actual_vs_predicted.png'))
        plt.close()
    except Exception as e:
        logger.error(f"Error plotting actual vs predicted: {e}")
        raise

def calculate_metrics(y_test, y_pred, place):
    try:
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        logger.info(f"Metrics for {place}:")
        logger.info(f"Mean Absolute Error (MAE): {mae}")
        logger.info(f"Mean Squared Error (MSE): {mse}")
        logger.info(f"R-squared (R²): {r2}")
        return {'city': place, 'mean_absolute_error': mae, 'mean_squared_error': mse, 'r_squared': r2, 'date_added': datetime.now().date(), 'time_added': datetime.now().time()}
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        raise

def save_predictions(predictions, file_path):
    try:
        logger.info("Saving predictions to CSV")
        predictions_df = pd.DataFrame(predictions)
        predictions_df.to_csv(file_path, index=False)
    except Exception as e:
        logger.error(f"Error saving predictions: {e}")
        raise

def plot_predictions(predictions_df):
    try:
        for place in predictions_df['Place'].unique():
            logger.info(f"Plotting predictions for {place}")
            place_data = predictions_df[predictions_df['Place'] == place]
            plt.figure(figsize=(10, 6))
            plt.plot(place_data['Date'], place_data['Predicted Heat Index'], marker='o', label=place)
            plt.xlabel('Date')
            plt.ylabel('Predicted Heat Index')
            plt.title(f'Predicted Heat Index for the Next 7 Days in {place}')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            date_today = datetime.now().strftime('%Y-%m-%d')
            output_dir = os.path.join(root_dir, 'charts', 'predicted_heat_index', date_today)
            os.makedirs(output_dir, exist_ok=True)
            plt.savefig(os.path.join(output_dir, f'{place}_predicted_heat_index.png'))
            plt.close()

        logger.info("Plotting combined predictions")
        plt.figure(figsize=(10, 6))
        for place in predictions_df['Place'].unique():
            place_data = predictions_df[predictions_df['Place'] == place]
            plt.plot(place_data['Date'], place_data['Predicted Heat Index'], marker='o', label=place)

        plt.xlabel('Date')
        plt.ylabel('Predicted Heat Index')
        plt.title('Predicted Heat Index for the Next 7 Days')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        date_today = datetime.now().strftime('%Y-%m-%d')
        plt.savefig(os.path.join(root_dir, 'charts', 'predicted_heat_index', date_today, f'{date_today}_overall_heat_index.png'))
        plt.close()
    except Exception as e:
        logger.error(f"Error plotting predictions: {e}")
        raise

def save_to_database(predictions_df, metrics_df):
    try:
        load_dotenv()

        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        cursor = connection.cursor()

        # Transfer previous data from weatherdataforecast to weatherdataforecasthistory
        cursor.execute("INSERT INTO weatherdataforecasthistory (city, hi_day_one, hi_level_day_one, hi_day_two, hi_level_day_two, hi_day_three, hi_level_day_three, hi_day_four, hi_level_day_four, hi_day_five, hi_level_day_five, hi_day_six, hi_level_day_six, hi_day_seven, hi_level_day_seven, date_added, time_added) SELECT city, hi_day_one, hi_level_day_one, hi_day_two, hi_level_day_two, hi_day_three, hi_level_day_three, hi_day_four, hi_level_day_four, hi_day_five, hi_level_day_five, hi_day_six, hi_level_day_six, hi_day_seven, hi_level_day_seven, date_added, time_added FROM weatherdataforecast")
        cursor.execute("DELETE FROM weatherdataforecast")

        # Transfer previous data from predictedhimetrics to predictedhimetricshistory
        cursor.execute("INSERT INTO predictedhimetricshistory (city, mean_absolute_error, mean_squared_error, r_squared, prediction_rating, date_added, time_added) SELECT city, mean_absolute_error, mean_squared_error, r_squared, prediction_rating, date_added, time_added FROM predictedhimetrics")
        cursor.execute("DELETE FROM predictedhimetrics")

        for place in predictions_df['Place'].unique():
            place_data = predictions_df[predictions_df['Place'] == place]
            hi_day_one = float(place_data.iloc[0]['Predicted Heat Index'])
            hi_day_two = float(place_data.iloc[1]['Predicted Heat Index'])
            hi_day_three = float(place_data.iloc[2]['Predicted Heat Index'])
            hi_day_four = float(place_data.iloc[3]['Predicted Heat Index'])
            hi_day_five = float(place_data.iloc[4]['Predicted Heat Index'])
            hi_day_six = float(place_data.iloc[5]['Predicted Heat Index'])
            hi_day_seven = float(place_data.iloc[6]['Predicted Heat Index'])
            date_added = datetime.now().date()
            time_added = datetime.now().time()

            query = """
            INSERT INTO weatherdataforecast (city, hi_day_one, hi_day_two, hi_day_three, hi_day_four, hi_day_five, hi_day_six, hi_day_seven, date_added, time_added)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (place, hi_day_one, hi_day_two, hi_day_three, hi_day_four, hi_day_five, hi_day_six, hi_day_seven, date_added, time_added))

        for index, row in metrics_df.iterrows():
            query = """
            INSERT INTO predictedhimetrics (city, mean_absolute_error, mean_squared_error, r_squared, date_added, time_added)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (row['city'], row['mean_absolute_error'], row['mean_squared_error'], row['r_squared'], row['date_added'], row['time_added']))

        connection.commit()
        cursor.close()
        connection.close()
        logger.info("Predictions and metrics saved to database")
    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")
        if connection.is_connected():
            cursor.close()
            connection.close()
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_model(model, model_name):
    try:
        date_today = datetime.now().strftime('%Y-%m-%d')
        model_dir = os.path.join(parent_root_dir, 'models', 'heat_index_prediction', date_today)
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, model_name)
        joblib.dump(model, model_path)
        logger.info(f"Model - {model_name} saved successfully - {date_today}")
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        raise

def main():
    try:
        start_time = time.time()
        date_today = datetime.now().strftime('%Y-%m-%d')
        file_path = os.path.join(root_dir, 'data', 'historical_weather_data', f'{date_today}_weather_data.csv')
        data = load_data(file_path)
        
        required_columns = {'Place', 'Date', 'Heat Index', 'Temperature Max', 'Temperature Min', 'Apparent Temperature Max', 'Apparent Temperature Mean', 'Precipitation', 'Wind Speed Max', 'Solar Radiation'}
        data = check_required_columns(data, required_columns)
        
        grouped = data.groupby('Place')
        predictions = []
        metrics = []
        start_date = datetime.now() + timedelta(days=1)
        date_range = [start_date + timedelta(days=i) for i in range(7)]
        
        batch_size = 10
        groups = list(grouped)
        for i in range(0, len(groups), batch_size):
            batch_groups = groups[i:i + batch_size]
            for place, group in batch_groups:
                try:
                    logger.info(f"Processing data for {place}")
                    group = prepare_data_for_regression(group)
                    
                    features = ['day', 'Temperature Max', 'Temperature Min', 'Apparent Temperature Max', 'Apparent Temperature Mean', 'Precipitation', 'Wind Speed Max', 'Solar Radiation']
                    X = group[features]
                    y = group['Heat Index']
                    
                    logger.info("Splitting the data into training and testing sets")
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                    
                    model = train_model(X_train, y_train)
                    varied_predictions = make_predictions(model, group, date_range, features)
                    
                    for date, prediction in zip(date_range, varied_predictions):
                        predictions.append({'Place': place, 'Date': date, 'Predicted Heat Index': prediction})
                    
                    y_pred = model.predict(X_test)
                    plot_actual_vs_predicted(X_test, y_test, y_pred, place)
                    metrics.append(calculate_metrics(y_test, y_pred, place))
                    
                    save_model(model, f"{place}_heat_index_model.pkl")
                except Exception as e:
                    logger.error(f"Error processing data for {place}: {e}")
        
        date_today = datetime.now().strftime('%Y-%m-%d')
        save_predictions(predictions, os.path.join(root_dir, 'data', 'predicted_heat_index', f'{date_today}_heat_index_prediction.csv'))
        predictions_df = pd.DataFrame(predictions)
        metrics_df = pd.DataFrame(metrics)
        plot_predictions(predictions_df)
        save_to_database(predictions_df, metrics_df)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Total time taken for the process to complete: {elapsed_time:.2f} seconds")
        logger.info("Process completed")
    except Exception as e:
        logger.error(f"Error in main process: {e}")

if __name__ == "__main__":
    main()