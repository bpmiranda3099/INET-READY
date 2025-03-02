import numpy as np
import xgboost as xgb
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.metrics import mean_squared_error
from loguru import logger
import multiprocessing

def perform_nested_cv_with_param_tuning(X, y, param_grid):
    """
    Perform nested cross-validation with hyperparameter tuning
    """
    try:
        logger.info("Performing nested cross-validation with hyperparameter tuning")
        
        # Use all available cores for GridSearchCV
        n_jobs = min(4, multiprocessing.cpu_count())
        
        # Outer loop
        outer_cv = KFold(n_splits=5, shuffle=True, random_state=42)
        inner_cv = KFold(n_splits=3, shuffle=True, random_state=42)
        
        outer_scores = []
        best_params_list = []
        
        for train_idx, test_idx in outer_cv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Inner loop for hyperparameter tuning
            model = GridSearchCV(
                estimator=xgb.XGBRegressor(
                    objective='reg:squarederror',
                    verbosity=0  # Reduce verbosity for speed
                ),
                param_grid=param_grid,
                cv=inner_cv,
                scoring='neg_mean_squared_error',
                n_jobs=n_jobs,
                error_score='raise',
                refit=True,
                verbose=0
            )
            model.fit(X_train, y_train)
            
            # Get best model from hyperparameter tuning
            best_params = model.best_params_
            best_params_list.append(best_params)
            logger.info(f"Best parameters found: {best_params}")
            
            # Evaluate on the test set
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            outer_scores.append(mse)
        
        # Aggregate best parameters across folds - take the most common value for each parameter
        final_best_params = {}
        for param in param_grid.keys():
            param_values = [params[param] for params in best_params_list]
            # Get the most common value
            unique_values, counts = np.unique(param_values, return_counts=True)
            final_best_params[param] = unique_values[np.argmax(counts)]
        
        logger.info(f"Nested CV results - Mean MSE: {np.mean(outer_scores):.4f}, Std MSE: {np.std(outer_scores):.4f}")
        logger.info(f"Final best parameters: {final_best_params}")
        return np.mean(outer_scores), np.std(outer_scores), final_best_params
    except Exception as e:
        logger.error(f"Error in nested cross-validation: {e}")
        raise
