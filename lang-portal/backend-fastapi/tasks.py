import click
from tasks.init_db import init_db

@click.group()
def cli():
    """Task runner for Lang Portal backend"""
    pass

@cli.command()
def init_db_task():
    """Initialize the SQLite database"""
    init_db()

@cli.command()
def migrate():
    """Run database migrations"""
    from tasks.migrate_db import migrate_db
    migrate_db()

@cli.command()
def seed():
    """Seed database with initial data"""
    import asyncio
    from tasks.seed_data import seed_data
    asyncio.run(seed_data())

if __name__ == "__main__":
    cli() 