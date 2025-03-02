import numpy as np
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from loguru import logger

def perform_k_fold_cross_validation(X, y, model, n_splits=5):
    """
    Perform k-fold cross-validation and return results
    """
    try:
        logger.info(f"Performing {n_splits}-fold cross-validation")
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        mae_scores = []
        mse_scores = []
        r2_scores = []
        
        for train_index, test_index in kf.split(X):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            mae_scores.append(mean_absolute_error(y_test, y_pred))
            mse_scores.append(mean_squared_error(y_test, y_pred))
            r2_scores.append(r2_score(y_test, y_pred))
        
        cv_results = {
            'mean_mae': np.mean(mae_scores),
            'std_mae': np.std(mae_scores),
            'mean_mse': np.mean(mse_scores),
            'std_mse': np.std(mse_scores),
            'mean_r2': np.mean(r2_scores),
            'std_r2': np.std(r2_scores)
        }
        
        logger.info(f"Cross-validation results: MAE={cv_results['mean_mae']:.4f}±{cv_results['std_mae']:.4f}, " 
                   f"MSE={cv_results['mean_mse']:.4f}±{cv_results['std_mse']:.4f}, "
                   f"R²={cv_results['mean_r2']:.4f}±{cv_results['std_r2']:.4f}")
        
        return cv_results
    except Exception as e:
        logger.error(f"Error performing cross-validation: {e}")
        raise
