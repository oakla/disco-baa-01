"""
Utility functions for data science operations
"""

import pandas as pd
import numpy as np
import random
from pathlib import Path
from typing import Union


def load_data(filepath: Union[str, Path]) -> pd.DataFrame:
    """
    Load data from a CSV file.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame containing the loaded data
    """
    return pd.read_csv(filepath)


def save_data(df: pd.DataFrame, filepath: Union[str, Path]) -> None:
    """
    Save DataFrame to a CSV file.
    
    Args:
        df: DataFrame to save
        filepath: Path where the CSV file will be saved
    """
    df.to_csv(filepath, index=False)


def describe_data(df: pd.DataFrame) -> dict:
    """
    Generate basic statistics about the dataset.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dictionary with basic statistics
    """
    return {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "memory_usage": df.memory_usage(deep=True).sum()
    }


def set_random_seed(seed: int = 42) -> None:
    """
    Set random seed for reproducibility across multiple libraries.
    
    Args:
        seed: Random seed value
    """
    random.seed(seed)
    np.random.seed(seed)
