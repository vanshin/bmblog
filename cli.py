import click
from models.database import migrate_db, init_db, create_tables

@click.group()
def cli():
    """Database management commands"""
    pass

@cli.command()
def db_migrate():
    """Run database migrations"""
    migrate_db()
    click.echo("Database migration completed!")

@cli.command()
def db_init():
    """Initialize database with default data"""
    init_db()
    click.echo("Database initialized!")

@cli.command()
def db_create():
    """Create database tables"""
    create_tables()
    click.echo("Database tables created!")

if __name__ == '__main__':
    cli() 