import sqlite3
import os
from pathlib import Path

def init_db():
    """Initialize the SQLite database"""
    # Get the root directory
    root_dir = Path(__file__).parent.parent
    db_path = root_dir / 'words.db'
    
    try:
        # Create database file if it doesn't exist
        conn = sqlite3.connect(db_path)
        
        # Set proper file permissions
        os.chmod(db_path, 0o644)
        
        # Create a test connection to verify
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print(f"✅ Database initialized successfully at {db_path}")
        print("✅ Foreign key constraints enabled")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    init_db() 