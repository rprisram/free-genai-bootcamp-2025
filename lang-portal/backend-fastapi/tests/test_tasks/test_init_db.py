import pytest
import os
from pathlib import Path
from tasks.init_db import init_db

def test_init_db(tmp_path):
    # Set up test environment
    os.chdir(tmp_path)
    db_path = Path("words.db")
    
    # Run init_db
    assert init_db() == True
    
    # Verify database was created
    assert db_path.exists()
    assert db_path.stat().st_size > 0

def test_init_db_existing(tmp_path):
    # Set up test environment
    os.chdir(tmp_path)
    db_path = Path("words.db")
    
    # Create dummy database
    db_path.touch()
    original_size = db_path.stat().st_size
    
    # Run init_db
    assert init_db() == True
    
    # Verify database was recreated
    assert db_path.stat().st_size != original_size 