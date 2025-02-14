import pytest
import os
from pathlib import Path
from alembic import command
from alembic.config import Config
from tasks.migrate_db import migrate_db

def test_migrate_db(tmp_path):
    # Set up test environment
    os.chdir(tmp_path)
    db_path = Path("words.db")
    
    # Create alembic.ini
    alembic_ini = tmp_path / "alembic.ini"
    alembic_ini.write_text("""
[alembic]
script_location = migrations
sqlalchemy.url = sqlite:///words.db
    """)
    
    # Create migrations directory
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    
    # Run migrations
    assert migrate_db() == True
    
    # Verify database was created with tables
    assert db_path.exists()
    assert db_path.stat().st_size > 0

def test_migrate_db_with_existing_db(tmp_path):
    # Set up test environment with existing database
    os.chdir(tmp_path)
    db_path = Path("words.db")
    db_path.touch()
    
    # Run migrations
    assert migrate_db() == True
    
    # Verify database was updated
    assert db_path.stat().st_size > 0 