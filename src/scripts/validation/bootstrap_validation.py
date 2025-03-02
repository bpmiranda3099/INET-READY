import numpy as np
from sklearn.utils import resample
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from loguru import logger

def bootstrap_evaluation(X, y, model, n_iterations=50):  # Reduced from 100 to 50 iterations for speed
    """
    Perform bootstrap evaluation of the model
    """
    try:
        logger.info(f"Performing bootstrap evaluation with {n_iterations} iterations")
        
        # Pre-allocate arrays for performance
        mae_scores = np.zeros(n_iterations)
        mse_scores = np.zeros(n_iterations)
        r2_scores = np.zeros(n_iterations)
        
        # Calculate the sample size once
        sample_size = int(0.8 * len(X))
        indices_pool = np.arange(len(X))
        
        for i in range(n_iterations):
            # Bootstrap sampling - more efficient implementation
            indices = resample(indices_pool, replace=True, n_samples=sample_size, random_state=i)
            test_mask = np.ones(len(X), dtype=bool)
            test_mask[indices] = False
            test_indices = np.where(test_mask)[0]
            
            X_train, y_train = X.iloc[indices], y.iloc[indices]
            X_test, y_test = X.iloc[test_indices], y.iloc[test_indices]
            
            # Train and evaluate
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mae_scores[i] = mean_absolute_error(y_test, y_pred)
            mse_scores[i] = mean_squared_error(y_test, y_pred)
            r2_scores[i] = r2_score(y_test, y_pred)
        
        # Calculate confidence intervals - vectorized operations
        bootstrap_results = {
            'mae': {
                'mean': np.mean(mae_scores),
                'std': np.std(mae_scores),
                'ci_lower': np.percentile(mae_scores, 2.5),
                'ci_upper': np.percentile(mae_scores, 97.5)
            },
            'mse': {
                'mean': np.mean(mse_scores),
                'std': np.std(mse_scores),
                'ci_lower': np.percentile(mse_scores, 2.5),
                'ci_upper': np.percentile(mse_scores, 97.5)
            },
            'r2': {
                'mean': np.mean(r2_scores),
                'std': np.std(r2_scores),
                'ci_lower': np.percentile(r2_scores, 2.5),
                'ci_upper': np.percentile(r2_scores, 97.5)
            }
        }
        
        logger.info(f"Bootstrap evaluation results:")
        logger.info(f"MAE: {bootstrap_results['mae']['mean']:.4f} (95% CI: {bootstrap_results['mae']['ci_lower']:.4f}-{bootstrap_results['mae']['ci_upper']:.4f})")
        logger.info(f"MSE: {bootstrap_results['mse']['mean']:.4f} (95% CI: {bootstrap_results['mse']['ci_lower']:.4f}-{bootstrap_results['mse']['ci_upper']:.4f})")
        logger.info(f"R²: {bootstrap_results['r2']['mean']:.4f} (95% CI: {bootstrap_results['r2']['ci_lower']:.4f}-{bootstrap_results['r2']['ci_upper']:.4f})")
        
        return bootstrap_results
    except Exception as e:
        logger.error(f"Error in bootstrap evaluation: {e}")
        raise
