from sklearn.inspection import permutation_importance
from loguru import logger

def perform_permutation_test(X, y, model, n_repeats=10):
    """
    Perform permutation feature importance test
    """
    try:
        logger.info("Performing permutation feature importance test")
        
        # Train the model
        model.fit(X, y)
        
        # Calculate baseline score
        baseline_score = model.score(X, y)
        logger.info(f"Baseline model R² score: {baseline_score:.4f}")
        
        # Calculate permutation importance
        r = permutation_importance(model, X, y, n_repeats=n_repeats, random_state=42)
        
        # Summarize feature importance
        feature_importance = {}
        for i in range(len(X.columns)):
            feature = X.columns[i]
            score_mean = r.importances_mean[i]
            score_std = r.importances_std[i]
            feature_importance[feature] = {
                'importance': score_mean,
                'std': score_std
            }
            logger.info(f"Feature: {feature}, Importance: {score_mean:.4f} ± {score_std:.4f}")
            
        # Sort features by importance
        sorted_importance = sorted(
            feature_importance.items(), 
            key=lambda x: x[1]['importance'], 
            reverse=True
        )
        
        # Log the most important features
        logger.info(f"Top features by importance:")
        for feature, stats in sorted_importance:
            logger.info(f"{feature}: {stats['importance']:.4f}")
            
        return feature_importance
    except Exception as e:
        logger.error(f"Error in permutation test: {e}")
        raise
