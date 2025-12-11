"""
Tests for utility functions
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from disco_baa_01.utils import (
    load_data,
    save_data,
    describe_data,
    set_random_seed
)


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing"""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'value': [10.5, 20.3, 30.1, 40.8, 50.2],
        'category': ['A', 'B', 'A', 'C', 'B']
    })


def test_describe_data(sample_dataframe):
    """Test the describe_data function"""
    stats = describe_data(sample_dataframe)
    
    assert 'shape' in stats
    assert 'columns' in stats
    assert 'dtypes' in stats
    assert 'missing_values' in stats
    assert 'memory_usage' in stats
    
    assert stats['shape'] == (5, 3)
    assert len(stats['columns']) == 3
    assert 'id' in stats['columns']


def test_set_random_seed():
    """Test that setting random seed produces reproducible results"""
    set_random_seed(42)
    result1 = np.random.rand(5)
    
    set_random_seed(42)
    result2 = np.random.rand(5)
    
    np.testing.assert_array_equal(result1, result2)


def test_save_and_load_data(sample_dataframe):
    """Test saving and loading data"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_path = f.name
    
    try:
        # Save data
        save_data(sample_dataframe, temp_path)
        
        # Load data
        loaded_df = load_data(temp_path)
        
        # Verify data integrity
        pd.testing.assert_frame_equal(sample_dataframe, loaded_df)
    finally:
        # Clean up
        Path(temp_path).unlink(missing_ok=True)


def test_describe_data_with_missing_values():
    """Test describe_data with missing values"""
    df = pd.DataFrame({
        'a': [1, 2, None, 4],
        'b': [5, None, 7, 8]
    })
    
    stats = describe_data(df)
    
    assert stats['missing_values']['a'] == 1
    assert stats['missing_values']['b'] == 1
