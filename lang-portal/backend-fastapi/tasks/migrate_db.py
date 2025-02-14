import os
from pathlib import Path
from alembic import command
from alembic.config import Config

def migrate_db():
    """Run database migrations"""
    try:
        # Get root directory and create alembic.ini path
        root_dir = Path(__file__).parent.parent
        alembic_cfg = Config(str(root_dir / "alembic.ini"))
        
        # Set migrations directory
        alembic_cfg.set_main_option("script_location", str(root_dir / "migrations"))
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite+aiosqlite:///{root_dir}/words.db")
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        
        print("✅ Database migrations completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error running migrations: {str(e)}")
        return False

if __name__ == "__main__":
    migrate_db() 