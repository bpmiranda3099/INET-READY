import xgboost as xgb
from loguru import logger
from tqdm import tqdm

from .k_fold_validation import perform_k_fold_cross_validation
from .nested_cv_validation import perform_nested_cv_with_param_tuning
from .bootstrap_validation import bootstrap_evaluation
from .permutation_validation import perform_permutation_test
from .time_based_validation import perform_time_based_validation

def validate_model(city, data, features, target='Heat Index'):
    """
    Comprehensive model validation using multiple techniques
    """
    try:
        tqdm.write(f"🔍 Checking accuracy for {city} forecast")
        
        X = data[features]
        y = data[target]
        
        # Create a progress bar for validation steps
        with tqdm(total=5, desc=f"Testing {city} data", leave=False, position=1) as pbar:
            # Basic model
            model = xgb.XGBRegressor(objective='reg:squarederror')
            
            # 1. K-fold cross-validation
            cv_results = perform_k_fold_cross_validation(X, y, model, n_splits=5)
            pbar.update(1)
            
            # 2. Nested cross-validation with hyperparameter tuning
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.2]
            }
            nested_cv_mse, nested_cv_mse_std, best_params = perform_nested_cv_with_param_tuning(X, y, param_grid)
            pbar.update(1)
            
            # 3. Bootstrap evaluation
            bootstrap_results = bootstrap_evaluation(X, y, model)
            pbar.update(1)
            
            # 4. Permutation test for feature importance
            feature_importance = perform_permutation_test(X, y, model)
            pbar.update(1)
            
            # 5. Time-based validation if data has dates
            time_cv_results = perform_time_based_validation(data, features, target)
            pbar.update(1)
            
            # Compile all validation results
            validation_results = {
                'city': city,
                'cross_validation': cv_results,
                'nested_cv': {
                    'mean_mse': nested_cv_mse,
                    'std_mse': nested_cv_mse_std,
                    'best_params': best_params
                },
                'bootstrap': bootstrap_results,
                'feature_importance': feature_importance,
                'time_cv': time_cv_results
            }
            
        tqdm.write(f"✅ Forecast validation complete for {city}")
        return validation_results
    except Exception as e:
        tqdm.write(f"⚠️ Trouble checking {city} data: {str(e).split(':')[0]}")
        logger.error(f"Error in model validation for {city}: {e}")
        raise
